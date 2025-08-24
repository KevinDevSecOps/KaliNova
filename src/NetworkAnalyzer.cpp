cat > src/network_analyzer/NetworkAnalyzer.cpp << 'EOL'
#include "NetworkAnalyzer.h"
#include <iostream>
#include <iomanip>
#include <fstream>
#include <ctime>

NetworkAnalyzer::NetworkAnalyzer() : pcapHandle(nullptr) {}

NetworkAnalyzer::~NetworkAnalyzer() {
    stopCapture();
    if (pcapHandle) {
        pcap_close(pcapHandle);
    }
}

bool NetworkAnalyzer::startCapture(const std::string& interface, int timeoutMs) {
    char errbuf[PCAP_ERRBUF_SIZE];
    
    // Abrir interface de red
    pcapHandle = pcap_open_live(interface.c_str(), BUFSIZ, 1, timeoutMs, errbuf);
    if (!pcapHandle) {
        std::cerr << "Error opening interface " << interface << ": " << errbuf << std::endl;
        return false;
    }
    
    // Compilar y aplicar filtro (opcional: capturar solo TCP/UDP)
    struct bpf_program fp;
    std::string filter = "tcp or udp or icmp";
    if (pcap_compile(pcapHandle, &fp, filter.c_str(), 0, PCAP_NETMASK_UNKNOWN) == -1) {
        std::cerr << "Error compiling filter: " << pcap_geterr(pcapHandle) << std::endl;
        return false;
    }
    
    if (pcap_setfilter(pcapHandle, &fp) == -1) {
        std::cerr << "Error setting filter: " << pcap_geterr(pcapHandle) << std::endl;
        return false;
    }
    
    pcap_freecode(&fp);
    
    // Iniciar captura en un hilo separado
    capturing = true;
    captureThread = std::thread([this]() {
        std::cout << "Starting network capture..." << std::endl;
        pcap_loop(pcapHandle, 0, packetHandler, reinterpret_cast<u_char*>(this));
    });
    
    return true;
}

void NetworkAnalyzer::stopCapture() {
    if (capturing) {
        capturing = false;
        if (pcapHandle) {
            pcap_breakloop(pcapHandle);
        }
        if (captureThread.joinable()) {
            captureThread.join();
        }
        std::cout << "Network capture stopped." << std::endl;
    }
}

void NetworkAnalyzer::packetHandler(u_char* userData, const struct pcap_pkthdr* pkthdr, const u_char* packet) {
    NetworkAnalyzer* analyzer = reinterpret_cast<NetworkAnalyzer*>(userData);
    analyzer->processPacket(pkthdr, packet);
}

void NetworkAnalyzer::processPacket(const struct pcap_pkthdr* pkthdr, const u_char* packet) {
    // Obtener cabecera Ethernet
    const struct ether_header* ethHeader = (struct ether_header*)packet;
    
    // Solo procesar paquetes IP
    if (ntohs(ethHeader->ether_type) != ETHERTYPE_IP) {
        return;
    }
    
    // Obtener cabecera IP
    const struct ip* ipHeader = (struct ip*)(packet + sizeof(struct ether_header));
    std::string srcIp = inet_ntoa(ipHeader->ip_src);
    std::string dstIp = inet_ntoa(ipHeader->ip_dst);
    
    // Actualizar estadísticas
    {
        std::lock_guard<std::mutex> lock(statsMutex);
        packetCount[srcIp]++;
        trafficVolume[srcIp] += pkthdr->len;
    }
    
    // Procesar según protocolo
    if (ipHeader->ip_p == IPPROTO_TCP) {
        const struct tcphdr* tcpHeader = (struct tcphdr*)(packet + sizeof(struct ether_header) + (ipHeader->ip_hl * 4));
        uint16_t dstPort = ntohs(tcpHeader->th_dport);
        
        {
            std::lock_guard<std::mutex> lock(statsMutex);
            destinationPorts[srcIp][dstPort]++;
        }
        
        detectPortScan(srcIp, dstIp, dstPort);
    }
    else if (ipHeader->ip_p == IPPROTO_UDP) {
        const struct udphdr* udpHeader = (struct udphdr*)(packet + sizeof(struct ether_header) + (ipHeader->ip_hl * 4));
        uint16_t dstPort = ntohs(udpHeader->uh_dport);
        
        {
            std::lock_guard<std::mutex> lock(statsMutex);
            destinationPorts[srcIp][dstPort]++;
        }
        
        // Detectar posible DNS amplification
        if (dstPort == 53) {
            detectDNSAmplification(srcIp, dstIp, pkthdr->len);
        }
    }
    
    detectDoS(srcIp, pkthdr->len);
}

void NetworkAnalyzer::detectPortScan(const std::string& srcIp, const std::string& dstIp, uint16_t dstPort) {
    static std::map<std::string, std::map<std::string, int>> scanAttempts;
    static std::map<std::string, std::chrono::steady_clock::time_point> lastReset;
    static std::mutex scanMutex;
    
    auto now = std::chrono::steady_clock::now();
    
    {
        std::lock_guard<std::mutex> lock(scanMutex);
        
        // Resetear contadores cada minuto por IP fuente
        if (now - lastReset[srcIp] > std::chrono::seconds(60)) {
            scanAttempts[srcIp].clear();
            lastReset[srcIp] = now;
        }
        
        scanAttempts[srcIp][dstIp]++;
        
        if (scanAttempts[srcIp][dstIp] > 25) {
            std::lock_guard<std::mutex> statsLock(statsMutex);
            anomalyDetections[srcIp] = "Possible port scan detected from " + srcIp + " to " + dstIp;
        }
    }
}

void NetworkAnalyzer::detectDoS(const std::string& srcIp, uint32_t packetSize) {
    static std::map<std::string, int> trafficVolume;
    static std::map<std::string, std::chrono::steady_clock::time_point> lastReset;
    static std::mutex dosMutex;
    
    auto now = std::chrono::steady_clock::now();
    
    {
        std::lock_guard<std::mutex> lock(dosMutex);
        
        // Resetear contadores cada 10 segundos por IP fuente
        if (now - lastReset[srcIp] > std::chrono::seconds(10)) {
            trafficVolume[srcIp] = 0;
            lastReset[srcIp] = now;
        }
        
        trafficVolume[srcIp] += packetSize;
        
        if (trafficVolume[srcIp] > 10 * 1024 * 1024) { // 10 MB en 10 segundos
            std::lock_guard<std::mutex> statsLock(statsMutex);
            anomalyDetections[srcIp] = "Possible DoS attack from " + srcIp;
        }
    }
}

void NetworkAnalyzer::detectDNSAmplification(const std::string& srcIp, const std::string& dstIp, uint32_t packetSize) {
    // Detectar posibles ataques de amplificación DNS
    static std::map<std::string, int> dnsQueryCount;
    static std::mutex dnsMutex;
    
    {
        std::lock_guard<std::mutex> lock(dnsMutex);
        dnsQueryCount[srcIp]++;
        
        if (dnsQueryCount[srcIp] > 100) { // Más de 100 consultas DNS por segundo
            std::lock_guard<std::mutex> statsLock(statsMutex);
            anomalyDetections[srcIp] = "Possible DNS amplification attack from " + srcIp;
        }
    }
}

void NetworkAnalyzer::printStats() const {
    std::lock_guard<std::mutex> lock(statsMutex);
    
    std::cout << "===== NETWORK ANALYSIS REPORT =====" << std::endl;
    std::cout << "Packets per source IP:" << std::endl;
    std::cout << std::setw(15) << "IP Address" << std::setw(10) << "Packets" << std::setw(12) << "Traffic" << std::endl;
    std::cout << "-----------------------------------" << std::endl;
    
    for (const auto& [ip, count] : packetCount) {
        double trafficMB = trafficVolume[ip] / (1024.0 * 1024.0);
        std::cout << std::setw(15) << ip 
                  << std::setw(10) << count 
                  << std::setw(10) << std::fixed << std::setprecision(2) << trafficMB << " MB" 
                  << std::endl;
    }
    
    std::cout << "\nAnomalies detected:" << std::endl;
    if (anomalyDetections.empty()) {
        std::cout << "No anomalies detected." << std::endl;
    } else {
        for (const auto& [ip, anomaly] : anomalyDetections) {
            std::cout << "• " << anomaly << std::endl;
        }
    }
    
    std::cout << "\nTop destination ports per IP:" << std::endl;
    for (const auto& [ip, ports] : destinationPorts) {
        std::cout << "IP " << ip << ":" << std::endl;
        for (const auto& [port, count] : ports) {
            std::cout << "  Port " << port << ": " << count << " packets" << std::endl;
        }
    }
}

void NetworkAnalyzer::saveToFile(const std::string& filename) const {
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error opening file: " << filename << std::endl;
        return;
    }
    
    std::lock_guard<std::mutex> lock(statsMutex);
    
    file << "Network Analysis Report - " << std::ctime(nullptr) << std::endl;
    file << "==========================================" << std::endl;
    
    file << "Packets per source IP:" << std::endl;
    for (const auto& [ip, count] : packetCount) {
        double trafficMB = trafficVolume[ip] / (1024.0 * 1024.0);
        file << ip << ": " << count << " packets, " << std::fixed << std::setprecision(2) << trafficMB << " MB" << std::endl;
    }
    
    file << "\nAnomalies detected:" << std::endl;
    for (const auto& [ip, anomaly] : anomalyDetections) {
        file << "• " << anomaly << std::endl;
    }
    
    file.close();
    std::cout << "Report saved to: " << filename << std::endl;
}
EOL
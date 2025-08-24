cat > src/network_analyzer/NetworkAnalyzer.h << 'EOL'
#ifndef NETWORKANALYZER_H
#define NETWORKANALYZER_H

#include <iostream>
#include <pcap.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <arpa/inet.h>
#include <map>
#include <chrono>
#include <thread>
#include <atomic>
#include <mutex>

class NetworkAnalyzer {
private:
    pcap_t* pcapHandle;
    std::atomic<bool> capturing{false};
    std::thread captureThread;
    std::mutex statsMutex;
    
    // Estadísticas
    std::map<std::string, int> packetCount;
    std::map<std::string, int> trafficVolume;
    std::map<std::string, std::map<uint16_t, int>> destinationPorts;
    std::map<std::string, std::string> anomalyDetections;
    
    // Métodos internos
    void processPacket(const struct pcap_pkthdr* pkthdr, const u_char* packet);
    void detectPortScan(const std::string& srcIp, const std::string& dstIp, uint16_t dstPort);
    void detectDoS(const std::string& srcIp, uint32_t packetSize);
    void detectDNSAmplification(const std::string& srcIp, const std::string& dstIp, uint32_t packetSize);
    
public:
    NetworkAnalyzer();
    ~NetworkAnalyzer();
    
    bool startCapture(const std::string& interface, int timeoutMs = 1000);
    void stopCapture();
    void printStats() const;
    void saveToFile(const std::string& filename) const;
    
    // Métodos estáticos
    static void packetHandler(u_char* userData, const struct pcap_pkthdr* pkthdr, const u_char* packet);
};

#endif
EOL
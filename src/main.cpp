cat > src/main.cpp << 'EOL'
#include <iostream>
#include <vector>
#include <string>
#include "vulnerability_scanner/VulnerabilityScanner.h"
#include "network_analyzer/NetworkAnalyzer.h"

void showBanner() {
    std::cout << "==========================================" << std::endl;
    std::cout << "            KALINOVA PENTEST SUITE        " << std::endl;
    std::cout << "       Advanced Security Tools in C++     " << std::endl;
    std::cout << "==========================================" << std::endl;
}

void showMenu() {
    std::cout << "\nMenu Principal:" << std::endl;
    std::cout << "1. Vulnerability Scanner" << std::endl;
    std::cout << "2. Network Analyzer" << std::endl;
    std::cout << "3. Advanced Fuzzer (Próximamente)" << std::endl;
    std::cout << "4. Salir" << std::endl;
    std::cout << "Selecciona una opción: ";
}

void runVulnerabilityScanner() {
    std::cout << "\n=== VULNERABILITY SCANNER ===" << std::endl;
    
    std::vector<std::string> targets;
    std::string target;
    
    std::cout << "Introduce los objetivos (escribe 'done' para terminar):" << std::endl;
    while (true) {
        std::cout << "Target: ";
        std::getline(std::cin, target);
        
        if (target == "done" || target.empty()) {
            break;
        }
        targets.push_back(target);
    }
    
    if (targets.empty()) {
        std::cout << "Usando objetivos de prueba por defecto..." << std::endl;
        targets = {"example.com", "testphp.vulnweb.com"};
    }
    
    VulnerabilityScanner scanner(targets);
    scanner.scanCommonVulnerabilities();
    scanner.generateReport();
}

void runNetworkAnalyzer() {
    std::cout << "\n=== NETWORK ANALYZER ===" << std::endl;
    
    NetworkAnalyzer analyzer;
    std::string interface;
    int duration;
    
    std::cout << "Interface de red (eth0, wlan0, etc.): ";
    std::getline(std::cin, interface);
    
    if (interface.empty()) {
        interface = "eth0";
    }
    
    std::cout << "Duración de captura (segundos): ";
    std::cin >> duration;
    std::cin.ignore(); // Limpiar buffer
    
    if (analyzer.startCapture(interface, 1000)) {
        std::cout << "Capturando tráfico durante " << duration << " segundos..." << std::endl;
        std::cout << "Presiona Ctrl+C para detener antes de tiempo." << std::endl;
        
        // Esperar el tiempo especificado
        for (int i = duration; i > 0; --i) {
            std::cout << "\rTiempo restante: " << i << " segundos" << std::flush;
            sleep(1);
        }
        std::cout << std::endl;
        
        analyzer.stopCapture();
        analyzer.printStats();
        
        std::string filename;
        std::cout << "Nombre del archivo para guardar el reporte (enter para omitir): ";
        std::getline(std::cin, filename);
        
        if (!filename.empty()) {
            analyzer.saveToFile(filename);
        }
    } else {
        std::cerr << "Error: No se pudo iniciar la captura en la interface " << interface << std::endl;
    }
}

int main() {
    showBanner();
    
    int choice;
    bool running = true;
    
    while (running) {
        showMenu();
        std::cin >> choice;
        std::cin.ignore(); // Limpiar buffer
        
        switch (choice) {
            case 1:
                runVulnerabilityScanner();
                break;
            case 2:
                runNetworkAnalyzer();
                break;
            case 3:
                std::cout << "Advanced Fuzzer estará disponible pronto." << std::endl;
                break;
            case 4:
                running = false;
                break;
            default:
                std::cout << "Opción no válida. Intenta de nuevo." << std::endl;
                break;
        }
    }
    
    std::cout << "Gracias por usar KaliNova. ¡Hasta pronto!" << std::endl;
    return 0;
}
EOL

cat > src/main.cpp << 'EOL'
#include <iostream>
#include <vector>
#include <string>
#include <thread>
#include <chrono>
#include "vulnerability_scanner/VulnerabilityScanner.h"
#include "network_analyzer/NetworkAnalyzer.h"
#include "advanced_fuzzer/AdvancedFuzzer.h"

void showBanner() {
    std::cout << "==========================================" << std::endl;
    std::cout << "            KALINOVA PENTEST SUITE        " << std::endl;
    std::cout << "       Advanced Security Tools in C++     " << std::endl;
    std::cout << "==========================================" << std::endl;
}

void showMenu() {
    std::cout << "\nMenu Principal:" << std::endl;
    std::cout << "1. Vulnerability Scanner" << std::endl;
    std::cout << "2. Network Analyzer" << std::endl;
    std::cout << "3. Advanced Fuzzer" << std::endl;
    std::cout << "4. Salir" << std::endl;
    std::cout << "Selecciona una opción: ";
}

void runVulnerabilityScanner() {
    std::cout << "\n=== VULNERABILITY SCANNER ===" << std::endl;
    
    std::vector<std::string> targets;
    std::string target;
    
    std::cout << "Introduce los objetivos (escribe 'done' para terminar):" << std::endl;
    while (true) {
        std::cout << "Target: ";
        std::getline(std::cin, target);
        
        if (target == "done" || target.empty()) {
            break;
        }
        targets.push_back(target);
    }
    
    if (targets.empty()) {
        std::cout << "Usando objetivos de prueba por defecto..." << std::endl;
        targets = {"example.com", "testphp.vulnweb.com"};
    }
    
    VulnerabilityScanner scanner(targets);
    scanner.scanCommonVulnerabilities();
    scanner.generateReport();
}

void runNetworkAnalyzer() {
    std::cout << "\n=== NETWORK ANALYZER ===" << std::endl;
    
    NetworkAnalyzer analyzer;
    std::string interface;
    int duration;
    
    std::cout << "Interface de red (eth0, wlan0, etc.): ";
    std::getline(std::cin, interface);
    
    if (interface.empty()) {
        interface = "eth0";
    }
    
    std::cout << "Duración de captura (segundos): ";
    std::cin >> duration;
    std::cin.ignore(); // Limpiar buffer
    
    if (analyzer.startCapture(interface, 1000)) {
        std::cout << "Capturando tráfico durante " << duration << " segundos..." << std::endl;
        std::cout << "Presiona Ctrl+C para detener antes de tiempo." << std::endl;
        
        // Esperar el tiempo especificado
        for (int i = duration; i > 0; --i) {
            std::cout << "\rTiempo restante: " << i << " segundos" << std::flush;
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
        std::cout << std::endl;
        
        analyzer.stopCapture();
        analyzer.printStats();
        
        std::string filename;
        std::cout << "Nombre del archivo para guardar el reporte (enter para omitir): ";
        std::getline(std::cin, filename);
        
        if (!filename.empty()) {
            analyzer.saveToFile(filename);
        }
    } else {
        std::cerr << "Error: No se pudo iniciar la captura en la interface " << interface << std::endl;
    }
}

void runAdvancedFuzzer() {
    std::cout << "\n=== ADVANCED FUZZER ===" << std::endl;
    
    AdvancedFuzzer fuzzer;
    std::string target_url;
    int threads;
    
    std::cout << "URL objetivo (ej: http://example.com): ";
    std::getline(std::cin, target_url);
    
    if (target_url.empty()) {
        std::cout << "Usando URL de prueba por defecto..." << std::endl;
        target_url = "http://testphp.vulnweb.com";
    }
    
    std::cout << "Número de hilos (recomendado: 5-10): ";
    std::cin >> threads;
    std::cin.ignore(); // Limpiar buffer
    
    if (threads <= 0) threads = 5;
    
    // Configurar el fuzzer
    FuzzConfig config;
    config.target_url = target_url;
    config.threads = threads;
    config.timeout_ms = 5000;
    config.delay_ms = 100;
    config.verbose = true;
    
    fuzzer.setConfig(config);
    
    // Añadir payloads por defecto
    auto sql_payloads = AdvancedFuzzer::generateSQLInjectionPayloads();
    auto xss_payloads = AdvancedFuzzer::generateXSSPayloads();
    auto lfi_payloads = AdvancedFuzzer::generateLFIpayloads();
    
    for (const auto& payload : sql_payloads) fuzzer.addPayload(payload);
    for (const auto& payload : xss_payloads) fuzzer.addPayload(payload);
    for (const auto& payload : lfi_payloads) fuzzer.addPayload(payload);
    
    std::cout << "Iniciando fuzzing contra: " << target_url << std::endl;
    std::cout << "Presiona Ctrl+C para detener." << std::endl;
    
    // Callback para mostrar resultados interesantes
    auto callback = [](const FuzzResult& result) {
        if (result.response_code == 200 || result.response_code >= 500) {
            std::cout << "[" << result.response_code << "] " << result.url << std::endl;
        }
    };
    
    fuzzer.startFuzzing(callback);
    fuzzer.printResults();
    
    std::string filename;
    std::cout << "Nombre del archivo para guardar el reporte (enter para omitir): ";
    std::getline(std::cin, filename);
    
    if (!filename.empty()) {
        fuzzer.saveResultsToFile(filename);
    }
}

int main() {
    showBanner();
    
    int choice;
    bool running = true;
    
    while (running) {
        showMenu();
        std::cin >> choice;
        std::cin.ignore(); // Limpiar buffer
        
        switch (choice) {
            case 1:
                runVulnerabilityScanner();
                break;
            case 2:
                runNetworkAnalyzer();
                break;
            case 3:
                runAdvancedFuzzer();
                break;
            case 4:
                running = false;
                break;
            default:
                std::cout << "Opción no válida. Intenta de nuevo." << std::endl;
                break;
        }
    }
    
    std::cout << "Gracias por usar KaliNova. ¡Hasta pronto!" << std::endl;
    return 0;
}
EOL
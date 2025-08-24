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
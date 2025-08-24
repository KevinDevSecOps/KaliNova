cat > src/advanced_fuzzer/test_fuzzer.cpp << 'EOL'
#include "AdvancedFuzzer.h"
#include <iostream>

// Callback personalizado para procesar respuestas
void responseCallback(const FuzzResult& result) {
    if (result.response_code == 200) {
        std::cout << "Found: " << result.url << " [200]" << std::endl;
    } else if (result.response_code >= 500) {
        std::cout << "Error: " << result.url << " [" << result.response_code << "]" << std::endl;
    }
}

int main() {
    std::cout << "Testing Advanced Fuzzer..." << std::endl;
    
    AdvancedFuzzer fuzzer;
    
    // Configurar el fuzzer
    FuzzConfig config;
    config.target_url = "http://testphp.vulnweb.com";
    config.threads = 5;
    config.timeout_ms = 3000;
    config.delay_ms = 100;
    config.verbose = true;
    
    fuzzer.setConfig(config);
    
    // Añadir algunos payloads personalizados
    fuzzer.addPayload("admin");
    fuzzer.addPayload("test");
    fuzzer.addPayload("config");
    
    // Añadir payloads de inyección SQL
    auto sql_payloads = AdvancedFuzzer::generateSQLInjectionPayloads();
    for (const auto& payload : sql_payloads) {
        fuzzer.addPayload(payload);
    }
    
    std::cout << "Starting fuzzing against: " << config.target_url << std::endl;
    std::cout << "Press Ctrl+C to stop early." << std::endl;
    
    // Iniciar fuzzing con callback personalizado
    fuzzer.startFuzzing(responseCallback);
    
    // Mostrar resultados
    fuzzer.printResults();
    
    // Guardar resultados en archivo
    fuzzer.saveResultsToFile("fuzzing_report.txt");
    
    // Mostrar vulnerabilidades encontradas
    auto vulnerabilities = fuzzer.getVulnerabilities();
    if (!vulnerabilities.empty()) {
        std::cout << "\nVulnerabilities found:" << std::endl;
        for (const auto& vuln : vulnerabilities) {
            std::cout << "• " << vuln.url << " [" << vuln.response_code << "]" << std::endl;
        }
    }
    
    return 0;
}
EOL
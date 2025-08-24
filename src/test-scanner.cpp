cat > src/vulnerability_scanner/test_scanner.cpp << 'EOL'
#include "VulnerabilityScanner.h"
#include <iostream>

int main() {
    std::cout << "Testing Vulnerability Scanner...\n";
    
    std::vector<std::string> testHosts = {
        "example.com",
        "testphp.vulnweb.com"
    };
    
    VulnerabilityScanner scanner(testHosts);
    scanner.scanCommonVulnerabilities();
    scanner.generateReport();
    
    return 0;
}
EOL
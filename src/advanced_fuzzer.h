cat > src/advanced_fuzzer/AdvancedFuzzer.h << 'EOL'
#ifndef ADVANCEDFUZZER_H
#define ADVANCEDFUZZER_H

#include <iostream>
#include <vector>
#include <string>
#include <thread>
#include <atomic>
#include <mutex>
#include <map>
#include <curl/curl.h>
#include <functional>
#include <queue>
#include <condition_variable>

// Estructura para resultados de fuzzing
struct FuzzResult {
    std::string payload;
    std::string url;
    long response_code;
    size_t response_size;
    double response_time;
    std::string notes;
    bool is_vulnerable;
};

// Estructura para configuración de fuzzing
struct FuzzConfig {
    std::string target_url;
    std::vector<std::string> wordlist;
    std::vector<std::string> extensions;
    std::map<std::string, std::string> headers;
    int timeout_ms;
    int threads;
    int delay_ms;
    bool follow_redirects;
    bool verbose;
};

// Callback type para procesamiento personalizado
using ResponseCallback = std::function<void(const FuzzResult&)>;

class AdvancedFuzzer {
private:
    FuzzConfig config;
    std::atomic<int> requests_sent{0};
    std::atomic<int> vulnerabilities_found{0};
    std::atomic<bool> stop_requested{false};
    std::mutex results_mutex;
    std::vector<FuzzResult> results;
    std::queue<std::string> payload_queue;
    std::mutex queue_mutex;
    std::condition_variable queue_cv;
    
    // Métodos internos
    size_t writeCallback(void* contents, size_t size, size_t nmemb, std::string* response);
    bool loadWordlist(const std::string& filename);
    void generatePayloads();
    void workerThread(int thread_id, ResponseCallback callback = nullptr);
    FuzzResult testPayload(const std::string& payload);
    bool analyzeResponse(const FuzzResult& result);
    void printProgressBar(int current, int total) const;
    
public:
    AdvancedFuzzer();
    ~AdvancedFuzzer();
    
    // Configuración
    void setConfig(const FuzzConfig& new_config);
    bool loadConfigFromFile(const std::string& filename);
    void addHeader(const std::string& name, const std::string& value);
    void addPayload(const std::string& payload);
    
    // Ejecución
    void startFuzzing(ResponseCallback callback = nullptr);
    void stopFuzzing();
    
    // Resultados
    void printResults() const;
    void saveResultsToFile(const std::string& filename) const;
    std::vector<FuzzResult> getResults() const;
    std::vector<FuzzResult> getVulnerabilities() const;
    
    // Utilidades
    static std::vector<std::string> generateNumberFuzz(int min, int max, int step = 1);
    static std::vector<std::string> generateStringFuzz(int min_len, int max_len);
    static std::vector<std::string> generateSQLInjectionPayloads();
    static std::vector<std::string> generateXSSPayloads();
    static std::vector<std::string> generateCommandInjectionPayloads();
    static std::vector<std::string> generatePathTraversalPayloads();
    static std::vector<std::string> generateLFIpayloads();
};

#endif
EOL
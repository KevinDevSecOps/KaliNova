import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ScanConfig:
    THREADS: int = 10
    TIMEOUT: int = 30
    RATE_LIMIT: int = 100  # requests per second
    USER_AGENT: str = "KaliNova-Scanner/1.0"
    OUTPUT_DIR: str = "outputs"

@dataclass
class APIConfig:
    VIRUS_TOTAL_API: str = os.getenv('VT_API_KEY', '')
    SHODAN_API: str = os.getenv('SHODAN_API_KEY', '')
    CENSYS_API: str = os.getenv('CENSYS_API_KEY', '')

class Wordlists:
    COMMON_PATHS = "/usr/share/wordlists/dirb/common.txt"
    SUBDOMAINS = "/usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-5000.txt"
    PASSWORDS = "/usr/share/wordlists/rockyou.txt"
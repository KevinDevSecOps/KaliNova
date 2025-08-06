# Exploit Report: {{CVE_ID}}  
- **Target**: {{TARGET_IP}}  
- **CVSS Score**: {{SCORE}}  
- **Steps**:  
  ```bash
  {{EXPLOIT_COMMANDS}}
  
**Uso**:  
```python
from jinja2 import Template

report = Template(open("templates/report.md").read()).render(
    CVE_ID="CVE-2023-1234",
    TARGET_IP="192.168.1.1",
    SCORE=9.8
)

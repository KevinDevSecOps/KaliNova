def send_alert(device, vulnerabilities):
    import requests
    webhook_url = "https://api.telegram.org/bot<TOKEN>/sendMessage"
    message = f"🚨 *NovaVision Alert*: {device} detectado\nVulnerabilidades: {', '.join(vulnerabilities)}"
    requests.post(webhook_url, json={"chat_id": <CHAT_ID>, "text": message})

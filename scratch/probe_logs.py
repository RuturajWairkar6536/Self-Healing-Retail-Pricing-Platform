import socket
import json
import time

def send_log(message, level="INFO"):
    log_entry = {
        "message": message,
        "loglevel": level,
        "tags": ["spe-api", "manual-probe"],
        "@timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 5000))
        s.sendall((json.dumps(log_entry) + "\n").encode('utf-8'))
        s.close()
        print(f"Sent: {message}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_log("System probe: Connecting K8s to ELK")
    send_log("Pricing API initialized", "INFO")
    send_log("Admin Dashboard heartbeat", "DEBUG")

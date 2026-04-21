import socket
import json
import time

WEBOTS_IP = "host.docker.internal"
WEBOTS_PORT = 5000

AUTH_TOKEN = "ECU_SECRET_123"

def send_to_vehicle(command):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(1.0)  # ✅ IMPORTANT

    t_start = time.perf_counter_ns()

    command["auth_token"] = AUTH_TOKEN

    client.connect((WEBOTS_IP, WEBOTS_PORT))
    client.sendall(json.dumps(command).encode())

    try:
        response = client.recv(1024).decode().strip()
    except socket.timeout:
        print("⚠️ No ACK (command dropped by security)")
        client.close()
        return None

    t_end = time.perf_counter_ns()
    latency_ms = (t_end - t_start) / 1_000_000
    print(f"[RTT] Cloud → Vehicle → Cloud : {latency_ms:.3f} ms")

    client.close()
    return json.loads(response)

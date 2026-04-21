from vehicle import Driver
import socket
import json
import time

# ===== RATE LIMITING CONFIG =====
RATE_WINDOW = 1.0
MAX_COMMANDS = 1

rate_window_start = time.time()
rate_command_count = 0

def rate_limit_ok():
    global rate_window_start, rate_command_count
    now = time.time()

    if now - rate_window_start > RATE_WINDOW:
        rate_window_start = now
        rate_command_count = 0

    if rate_command_count >= MAX_COMMANDS:
        return False

    rate_command_count += 1
    return True


# ===== SAFE ACTUATOR HELPERS =====
def set_headlights_safe(driver, state):
    """
    Try to control headlights safely.
    Returns True if supported, False otherwise.
    """
    if hasattr(driver, "setHeadlights"):
        driver.setHeadlights(state)
        return True
    return False


driver = Driver()

# ===== SECURITY CONFIG =====
AUTHORIZED_TOKEN = "ECU_SECRET_123"
ALLOWED_COMMANDS = {
    "SET_SPEED",
    "HEADLIGHT_ON",
    "HEADLIGHT_OFF",
    "HAZARD_ON",
    "HAZARD_OFF",
    "STATUS"
}

# ===== TCP SERVER =====
HOST = "0.0.0.0"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
server.setblocking(False)

print("Bridge ECU: Waiting for TCP connection...")

conn = None

while driver.step() != -1:
    if conn is None:
        try:
            conn, addr = server.accept()
            conn.setblocking(False)
            print(f"Bridge ECU: Connected to {addr}")
        except BlockingIOError:
            pass
    else:
        try:
            data = conn.recv(1024)
            if not data:
                continue

            # ===== RATE LIMIT =====
            if not rate_limit_ok():
                print("SECURITY: Rate limit exceeded — command dropped")
                continue

            msg = json.loads(data.decode())
            print("Bridge ECU received:", msg)

            # ===== AUTHORIZATION =====
            if msg.get("auth_token") != AUTHORIZED_TOKEN:
                print("SECURITY: Unauthorized command blocked")
                ack = {
                    "status": "DENIED",
                    "reason": "Invalid auth token"
                }
                conn.sendall(json.dumps(ack).encode())
                continue

            # ===== WHITELIST =====
            if msg.get("cmd") not in ALLOWED_COMMANDS:
                print("SECURITY: Command not allowed")
                ack = {
                    "status": "DENIED",
                    "reason": "Command not whitelisted"
                }
                conn.sendall(json.dumps(ack).encode())
                continue

            # ===== VEHICLE CONTROL =====
            if msg["cmd"] == "SET_SPEED":
                driver.setCruisingSpeed(float(msg["value"]))

            elif msg["cmd"] == "HEADLIGHT_ON":
                if not set_headlights_safe(driver, True):
                    ack = {
                        "status": "DENIED",
                        "reason": "Headlight actuator not supported"
                    }
                    conn.sendall(json.dumps(ack).encode())
                    continue

            elif msg["cmd"] == "HEADLIGHT_OFF":
                if not set_headlights_safe(driver, False):
                    ack = {
                        "status": "DENIED",
                        "reason": "Headlight actuator not supported"
                    }
                    conn.sendall(json.dumps(ack).encode())
                    continue

            elif msg["cmd"] == "HAZARD_ON":
                driver.setIndicator(Driver.INDICATOR_LEFT, True)
                driver.setIndicator(Driver.INDICATOR_RIGHT, True)

            elif msg["cmd"] == "HAZARD_OFF":
                driver.setIndicator(Driver.INDICATOR_LEFT, False)
                driver.setIndicator(Driver.INDICATOR_RIGHT, False)

            elif msg["cmd"] == "STATUS":
                pass

            # ===== ACK (VALID COMMANDS ONLY) =====
            ack = {
                "status": "OK",
                "applied_cmd": msg["cmd"]
            }
            conn.sendall(json.dumps(ack).encode())

        except BlockingIOError:
            # normal for non-blocking sockets
            pass
        except Exception as e:
            print("ECU error:", e)

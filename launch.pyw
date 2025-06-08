import os
import socket
import subprocess
import time
import webbrowser
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

# --- Settings ---
PORT = 5000
SCRIPT_NAME = "app.py"
URL = f"http://localhost:{PORT}"
LOG_FILE = "launcher.log"

# --- Logging ---
def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} - {msg}\n")

# --- Port Checking ---
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# --- Kill Flask on that port ---
def kill_flask():
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['cmdline'] and SCRIPT_NAME in ' '.join(proc.info['cmdline']):
                log(f"Killing process {proc.pid} running {SCRIPT_NAME}")
                proc.kill()
    except Exception as e:
        log(f"Error killing Flask: {e}")

# --- Start Flask ---
def start_server():
    if is_port_in_use(PORT):
        log(f"Port {PORT} already in use.")
        return
    log("Starting Flask server...")
    subprocess.Popen(["python", SCRIPT_NAME], shell=True)
    time.sleep(2)
    webbrowser.open(URL)

# --- Tray icon image ---
def create_image():
    image = Image.new("RGB", (64, 64), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill="black")
    return image

# --- Tray Setup ---
def run_tray():
    icon = pystray.Icon("FlaskLauncher")
    icon.icon = create_image()
    icon.title = "Flask Launcher"

    def quit_app(icon, item):
        log("Exiting tray...")
        icon.stop()

    def restart_app(icon, item):
        log("Restarting app...")
        kill_flask()
        time.sleep(1)
        start_server()

    icon.menu = pystray.Menu(
        item("Open App", lambda icon, item: webbrowser.open(URL)),
        item("Restart Server", restart_app),
        item("Quit", quit_app)
    )
    icon.run()

# --- MAIN ---
def main():
    log("=== Launcher started ===")
    if not is_port_in_use(PORT):
        start_server()
    else:
        log("Server already running, just opening browser.")
        webbrowser.open(URL)

    tray_thread = threading.Thread(target=run_tray)
    tray_thread.daemon = True
    tray_thread.start()

    # Keep main thread alive
    while tray_thread.is_alive():
        time.sleep(1)

main()

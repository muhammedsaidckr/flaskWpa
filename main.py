from flask import Flask, request, render_template
import requests
import subprocess
import time

app = Flask(__name__)

wifi_device = "wlan0"


@app.route('/')
def index():
    result = subprocess.check_output(
        ["nmcli", "--colors", "no", "-m", "multiline", "--get-value", "SSID", "dev", "wifi", "list", "ifname",
         wifi_device])
    ssids_list = result.decode().split('\n')
    ssids_cleaned = [ssid.removeprefix("SSID:") for ssid in ssids_list if len(ssid.removeprefix("SSID:")) > 0]
    return render_template('index.html', ssids=ssids_cleaned)


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        print(*list(request.form.keys()), sep=", ")
        ssid = request.form['ssid']
        password = request.form['password']
        connection_command = ["nmcli", "--colors", "no", "device", "wifi", "connect", ssid, "ifname", wifi_device]
        if len(password) > 0:
            connection_command.append("password")
            connection_command.append(password)
        result = subprocess.run(connection_command, capture_output=True)

        # restart the magicmirror service if it is not running
        # if the connection is successful
        if result.returncode == 0:
            print("reboot")
            subprocess.run(["sudo", "reboot"])


        message = ("Success: Connected to <i>{}</i>".format(ssid)) \
            if result.returncode == 0 \
            else "Error: Failed to connect to <i>{}</i>".format(ssid)
        # return if it is error or success
        return render_template('result.html', message=message, returncode=result.returncode)
    return "Error: HTTP Method not allowed."


def check_internet_connection():
    """Internet bağlantısını kontrol et"""
    try:
        requests.get('http://google.com', timeout=5)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False


def kill_process(port):
    """Belirli bir portu kullanan süreci sonlandır"""
    try:
        # netstat komutu ile belirli bir portu dinleyen sürecin PID'sini bul
        result = subprocess.check_output(["sudo", "netstat", "-tulnp"]).decode('utf-8')
        lines = result.splitlines()
        for line in lines:
            if f":{port}" in line:
                parts = line.split()
                pid = parts[-1].split("/")[0]
                print(f"{port} portunu kullanan süreç bulundu: PID {pid}. Sonlandırılıyor...")
                subprocess.run(["sudo", "kill", "-9", pid])
                print(f"PID {pid} sonlandırıldı.")
                return
        print(f"{port} portunu kullanan herhangi bir süreç bulunamadı.")
    except subprocess.CalledProcessError as e:
        print(f"Hata: {e.output}")


def start_magic_mirror_service():
    """Yeni uygulamayı başlat"""
    # Örnek olarak, bir HTTP sunucusunu belirli bir portta başlatma
    print("Yeni uygulama başlatılıyor...")
    subprocess.run(["sudo", "systemctl", "start", "magicmirror.service"])
    print("HTTP sunucusu 8080 portunda başlatıldı.")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)

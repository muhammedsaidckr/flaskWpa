from flask import Flask, render_template, request
import subprocess
import re

app = Flask(__name__)

def scan_wifi_networks():
    networks = []
    scan_output = subprocess.check_output(['sudo', 'iwlist', 'wlp0s20f3', 'scan']).decode('utf-8')
    network_blocks = scan_output.split('Cell')[1:]  # Her bir ağ bloğunu ayır
    for block in network_blocks:
        ssid_search = re.search(r'ESSID:"(.+)"', block)
        if ssid_search:
            networks.append(ssid_search.group(1))
    return networks

@app.route('/')
def index():
    available_networks = scan_wifi_networks()
    return render_template('index.html', networks=available_networks)

@app.route('/connect', methods=['POST'])
def connect():
    ssid = request.form['ssid']
    password = request.form['password']
    # wpa_supplicant.conf dosyasını güncelleyin
    config_lines = [
        '\nnetwork={',
        f'\tssid="{ssid}"',
        f'\tpsk="{password}"',
        '\tkey_mgmt=WPA-PSK',
        '}'
    ]
    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as wpa_file:
        wpa_file.writelines(config_lines)
    subprocess.run(['wpa_cli', '-i', 'wlan0', 'reconfigure'])
    return f'"{ssid}" ağına bağlanılmaya çalışılıyor...'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

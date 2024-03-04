from flask import Flask, request, render_template
import subprocess

app = Flask(__name__)

wifi_device = "wlp0s20f3"


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
        message = ("Success: Connected to <i>{}</i>".format(ssid)) \
            if result.returncode == 0 \
            else "Error: Failed to connect to <i>{}</i>".format(ssid)
        # return if it is error or success
        return render_template('result.html', message=message, returncode=result.returncode)
    return "Error: HTTP Method not allowed."


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)

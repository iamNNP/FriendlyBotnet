from flask import Flask, render_template, request
import paramiko

app = Flask(__name__)

# SSH details for the two Docker containers
CONTAINERS = [
    {"name": "alpine11", "host": "192.168.139.1", "port": 2222, "username": "root", "password": "password"},
    {"name": "alpine21", "host": "192.168.139.1", "port": 2221, "username": "root", "password": "password"},
    {"name": "alpine31", "host": "192.168.139.1", "port": 2220, "username": "root", "password": "password"}
]

def send_command_via_ssh(host, port, username, password, command):
    """Send a command to a remote server via SSH."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()
        return output, error
    except Exception as e:
        return None, str(e)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        command = request.form.get("command")
        for container in CONTAINERS:
            output, error = send_command_via_ssh(
                container["host"], container["port"], container["username"], container["password"], command
            )
            results.append({
                "name": container["name"],
                "output": output,
                "error": error,
            })
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
from django.shortcuts import render
from .forms import SSHCommandForm
import paramiko

# SSH details for the Docker containers
CONTAINERS = [
    {"name": "alpine11", "host": "localhost", "port": 2222, "username": "root", "password": "password"},
    {"name": "alpine21", "host": "localhost", "port": 2221, "username": "root", "password": "password"},
    {"name": "alpine31", "host": "localhost", "port": 2220, "username": "root", "password": "password"}
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

def index(request):
    results = []
    if request.method == "POST":
        form = SSHCommandForm(request.POST)
        if form.is_valid():
            command = form.cleaned_data['command']
            for container in CONTAINERS:
                output, error = send_command_via_ssh(
                    container["host"], container["port"], container["username"], container["password"], command
                )
                results.append({
                    "name": container["name"],
                    "output": output,
                    "error": error,
                })
    else:
        form = SSHCommandForm()
    
    return render(request, 'ssh_panel/index.html', {
        'form': form,
        'results': results
    })

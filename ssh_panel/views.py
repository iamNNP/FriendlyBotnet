from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from .forms import SSHCommandForm
import paramiko
import json
import time
import asyncio

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
        
        # Use get_pty=True to get line-buffered output
        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
        
        timeout = 30  # seconds
        start_time = time.time()
        
        # Read stdout
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                chunk = stdout.channel.recv(1024).decode()
                if chunk:
                    yield chunk
            
            if stderr.channel.recv_stderr_ready():
                chunk = stderr.channel.recv_stderr(1024).decode()
                if chunk:
                    yield f"ERROR: {chunk}"
            
            if time.time() - start_time > timeout:
                yield f"\nCommand timed out after {timeout} seconds"
                stdin.channel.close()
                break
            
            time.sleep(0.01)  # Small sleep to prevent CPU overuse
        
        # Read any remaining output
        while stdout.channel.recv_ready():
            chunk = stdout.channel.recv(1024).decode()
            if chunk:
                yield chunk
        
        while stderr.channel.recv_stderr_ready():
            chunk = stderr.channel.recv_stderr(1024).decode()
            if chunk:
                yield f"ERROR: {chunk}"
        
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            yield f"\nCommand exited with status {exit_status}"
        
        ssh.close()
    except Exception as e:
        yield f"ERROR: {str(e)}"

def stream_command_output(request):
    """Stream command output from all containers."""
    command = request.GET.get('command', '')
    if not command:
        return StreamingHttpResponse("No command provided", content_type='text/plain')
    
    def event_stream():
        for container in CONTAINERS:
            for output in send_command_via_ssh(container["host"], container["port"], container["username"], container["password"], command):
                yield f"data: {json.dumps({'container': container['name'], 'output': output})}\n\n"
        
    return StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )

def parse_ssh_file(file):
    """Parse uploaded SSH file and return a list of container dicts."""
    containers = []
    for line in file:
        try:
            line = line.decode('utf-8').strip()
            if not line or line.startswith('#'):
                continue
            name, host, port, username, password = line.split(':')
            containers.append({
                'name': name,
                'host': host,
                'port': int(port),
                'username': username,
                'password': password
            })
        except Exception:
            continue  # skip malformed lines
    return containers

def index(request):
    global CONTAINERS
    message = None
    if request.method == 'POST' and 'upload' in request.POST:
        form = SSHCommandForm(request.POST, request.FILES)
        if form.is_valid():
            ssh_file = form.cleaned_data.get('ssh_file')
            if ssh_file:
                containers = parse_ssh_file(ssh_file)
                if containers:
                    CONTAINERS = containers
                    message = f"Loaded {len(containers)} SSH connections from file."
                else:
                    message = "No valid SSH connections found in file."
    else:
        form = SSHCommandForm(request.POST or None)
    return render(request, 'ssh_panel/index.html', {
        'form': form,
        'message': message,
    })

def get_containers(request):
    """Return the list of container names as JSON."""
    return JsonResponse([c['name'] for c in CONTAINERS], safe=False)

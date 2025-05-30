from django.shortcuts import render
from django.http import StreamingHttpResponse
from .forms import SSHCommandForm
import paramiko
import json
import time

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
        buffer = ""
        
        while True:
            if stdout.channel.exit_status_ready():
                # Read any remaining output
                while stdout.channel.recv_ready():
                    chunk = stdout.channel.recv(1).decode()
                    if chunk == '\n':
                        yield buffer + '\n'
                        buffer = ""
                    else:
                        buffer += chunk
                if buffer:
                    yield buffer
                while stderr.channel.recv_stderr_ready():
                    chunk = stderr.channel.recv_stderr(1).decode()
                    if chunk == '\n':
                        yield f"ERROR: {buffer}\n"
                        buffer = ""
                    else:
                        buffer += chunk
                if buffer:
                    yield f"ERROR: {buffer}"
                break
            
            # Read available output
            if stdout.channel.recv_ready():
                chunk = stdout.channel.recv(1).decode()
                if chunk == '\n':
                    yield buffer + '\n'
                    buffer = ""
                else:
                    buffer += chunk
                    
            if stderr.channel.recv_stderr_ready():
                chunk = stderr.channel.recv_stderr(1).decode()
                if chunk == '\n':
                    yield f"ERROR: {buffer}\n"
                    buffer = ""
                else:
                    buffer += chunk
            
            if time.time() - start_time > timeout:
                if buffer:
                    yield buffer
                yield f"\nCommand timed out after {timeout} seconds"
                stdin.channel.close()
                break
            
            time.sleep(0.01)  # Small sleep to prevent CPU overuse
        
        if stdout.channel.exit_status_ready():
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
        container = CONTAINERS[0]
        for output in send_command_via_ssh(container["host"], container["port"], container["username"], container["password"], command):
            yield f"data: {json.dumps({'container': container['name'], 'output': output})}\n\n"
        
    return StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )

def index(request):
    form = SSHCommandForm()
    return render(request, 'ssh_panel/index.html', {
        'form': form,
    })

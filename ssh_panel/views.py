from django.shortcuts import render
from django.http import StreamingHttpResponse
from .forms import SSHCommandForm
import paramiko
import asyncio
import json
import time

# SSH details for the Docker containers
CONTAINERS = [
    {"name": "alpine11", "host": "localhost", "port": 2222, "username": "root", "password": "password"},
    {"name": "alpine21", "host": "localhost", "port": 2221, "username": "root", "password": "password"},
    {"name": "alpine31", "host": "localhost", "port": 2220, "username": "root", "password": "password"}
]

async def send_command_via_ssh(host, port, username, password, command):
    """Send a command to a remote server via SSH asynchronously."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        
        timeout = 30  # seconds
        start_time = time.time()
        
        while True:
            if stdout.channel.exit_status_ready():
                while stdout.channel.recv_ready():
                    chunk = stdout.channel.recv(256).decode()
                    yield chunk
                while stderr.channel.recv_stderr_ready():
                    chunk = stderr.channel.recv_stderr(256).decode()
                    yield f"ERROR: {chunk}"
                break
            
            if stdout.channel.recv_ready():
                chunk = stdout.channel.recv(256).decode()
                yield chunk
            if stderr.channel.recv_stderr_ready():
                chunk = stderr.channel.recv_stderr(256).decode()
                yield f"ERROR: {chunk}"
            
            if time.time() - start_time > timeout:
                yield f"\nCommand timed out after {timeout} seconds"
                stdin.channel.close()
                break
            
            await asyncio.sleep(0.1)
        
        if stdout.channel.exit_status_ready():
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                yield f"\nCommand exited with status {exit_status}"
        
        ssh.close()
    except Exception as e:
        yield f"ERROR: {str(e)}"

async def stream_command_output(request):
    """Stream command output from all containers."""
    command = request.GET.get('command', '')
    if not command:
        return StreamingHttpResponse("No command provided", content_type='text/plain')
    
    async def event_stream():
        # for container in CONTAINERS:
        #     yield f"data: {json.dumps({'container': container['name'], 'output': f'Starting command on {container["name"]}'})}\n\n"
        #     async for output in send_command_via_ssh(
        #         container["host"], container["port"], 
        #         container["username"], container["password"], 
        #         command
        #     ):
        #         yield f"data: {json.dumps({'container': container['name'], 'output': output})}\n\n"
        #     yield f"data: {json.dumps({'container': container['name'], 'output': 'Command completed'})}\n\n"\
        container = CONTAINERS[0]
        async for output in send_command_via_ssh(container["host"], container["port"], container["username"], container["password"], command):
            print(output)
            yield f"data: {json.dumps({'container': container['name'], 'output': output})}\n\n"
        yield f"data: {json.dumps({'container': container['name'], 'output': 'Command completed'})}\n\n"
    
    return StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )

def index(request):
    form = SSHCommandForm()
    return render(request, 'ssh_panel/index.html', {
        'form': form,
    })

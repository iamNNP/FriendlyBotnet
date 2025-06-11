from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from .forms import SSHCommandForm
from .models import CommandHistory
import paramiko
import json
import time
import asyncio
import concurrent.futures
import queue
import threading
from django.core import serializers

# SSH details for the Docker containers
CONTAINERS = []

stop_event = threading.Event()

def send_command_via_ssh(host, port, username, password, command):
    """Send a command to a remote server via SSH."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password)
        
        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
        
        while not stdout.channel.exit_status_ready():
            if stop_event.is_set():
                yield "\nCommand stopped by user."
                stdin.channel.close()
                break
            if stdout.channel.recv_ready():
                chunk = stdout.channel.recv(1024).decode()
                if chunk:
                    yield chunk
            if stderr.channel.recv_stderr_ready():
                chunk = stderr.channel.recv_stderr(1024).decode()
                if chunk:
                    yield f"ERROR: {chunk}"
            
            time.sleep(0.01)
        
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
    """Stream command output from selected containers asynchronously, line by line."""
    global stop_event
    stop_event.clear()
    command = request.GET.get('command', '')
    selected = request.GET.get('containers', '')
    selected_names = set(selected.split(',')) if selected else set(c['name'] for c in CONTAINERS)
    if not command:
        return StreamingHttpResponse("No command provided", content_type='text/plain')

    # Collect output from all containers
    all_output = []

    def event_stream():
        q = queue.Queue()
        threads = []

        def worker(container):
            try:
                for output in send_command_via_ssh(
                    container["host"], container["port"], container["username"], container["password"], command
                ):
                    for line in output.splitlines(True):
                        q.put((container['name'], line))
                    if stop_event.is_set():
                        break
            except Exception as e:
                q.put((container['name'], f"ERROR: {e}\n"))
            finally:
                q.put((container['name'], None))  # Signal this container is done

        # Only use selected containers
        for container in CONTAINERS:
            if container['name'] in selected_names:
                t = threading.Thread(target=worker, args=(container,))
                t.start()
                threads.append(t)

        finished = 0
        total = len(threads)
        while finished < total:
            try:
                name, output = q.get(timeout=0.1)
                if output is None:
                    finished += 1
                else:
                    all_output.append(f"[{name}] {output}")
                    yield f"data: {json.dumps({'container': name, 'output': output})}\n\n"
            except queue.Empty:
                continue

        for t in threads:
            t.join()

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )

    # After StreamingHttpResponse, save the command and output
    CommandHistory.objects.create(
        command=command,
        containers=",".join(selected_names),
        output="".join(all_output)
    )

    return response

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

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def stop_command(request):
    global stop_event
    stop_event.set()
    return JsonResponse({'status': 'stopped'})

def command_history(request):
    history = CommandHistory.objects.order_by('-timestamp')[:50]
    return render(request, 'ssh_panel/history.html', {'history': history})

def command_history_json(request):
    history = CommandHistory.objects.order_by('-timestamp')[:50]
    data = [
        {
            "command": h.command,
            "timestamp": h.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "containers": h.containers,
            "output": h.output,
        }
        for h in history
    ]
    return JsonResponse(data, safe=False)

import os

directories = [
    "friendlybotnet",
    "ssh_panel"
]

skip_dirs = {"__pycache__", "venv"}
skip_files = {"db.sqlite3", "code.py", "print_code.py", "Dockerfile", "Dockerfile.sshd", "manage.py", "code.txt", "containers.txt", "shortcuts.txt", "requirements.txt", "README.md", "docker-compose.yml"}

# Print files in listed directories (recursively)
for directory in directories:
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file in skip_files:
                continue
            file_path = os.path.join(root, file)
            print(f"\n=== {file_path} ===")
            try:
                with open(file_path, encoding="utf-8") as f:
                    print(f.read())
            except Exception as e:
                print(f"Could not read {file_path}: {e}")

# Print files in root directory (not in any folder)
for file in os.listdir('.'):
    if os.path.isfile(file) and file not in skip_files:
        print(f"\n=== {file} ===")
        try:
            with open(file, encoding="utf-8") as f:
                print(f.read())
        except Exception as e:
            print(f"Could not read {file}: {e}")
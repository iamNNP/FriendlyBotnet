# Start with base Arch Linux image
FROM archlinux:base-devel

# Update system and install Python with virtualenv
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm python python-pip python-virtualenv git && \
    pacman -Scc --noconfirm

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies in virtualenv
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port your Django app runs on
EXPOSE 8000

# Command to run when container starts
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
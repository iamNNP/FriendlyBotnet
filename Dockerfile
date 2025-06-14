FROM archlinux:base-devel

RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm python python-pip git && \
    pacman -Scc --noconfirm

RUN mkdir -p /usr/local/python-packages
ENV PYTHONPATH="/usr/local/python-packages"

WORKDIR /app
COPY requirements.txt .
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
FROM alpine:latest

# Install OpenSSH and set up root password
RUN apk add --no-cache openssh && \
    echo "root:password" | chpasswd && \
    ssh-keygen -A

# Configure SSH to allow root login
RUN sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config

# Expose SSH port
EXPOSE 22

# Start SSH server
CMD ["/usr/sbin/sshd", "-D"]


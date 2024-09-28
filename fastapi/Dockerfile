FROM python:3.11

# Install SSH server and other necessary packages
RUN apt-get update && apt-get install -y openssh-server
RUN mkdir /var/run/sshd

# SSH configuration
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && apt install -y nano curl wget
# Copy all files in the current directory to /app in the container
COPY . .

# List contents of /app for debugging
RUN ls -la /app

# Print Python version for debugging
RUN python --version

# Create a script to start services
RUN echo '#!/bin/bash\n\
mkdir -p /root/.ssh\n\
touch /root/.ssh/authorized_keys\n\
chmod 700 /root/.ssh\n\
chmod 600 /root/.ssh/authorized_keys\n\
\n\
# Add all SSH_PUBLIC_KEY_* to authorized_keys\n\
for var in $(compgen -A variable | grep ^SSH_PUBLIC_KEY_); do\n\
    echo "${!var}" | sed 's/\r$//' >> /root/.ssh/authorized_keys\n\
done\n\
\n\
service ssh start\n\
\n\
# Debug: List contents of /app again\n\
echo "Contents of /app:"\n\
ls -la /app\n\
\n\
# Debug: Print Python path\n\
echo "Python path:"\n\
python -c "import sys; print(sys.path)"\n\
\n\
# Start FastAPI application\n\
uvicorn main:app --host 0.0.0.0 --port 8000\n\
' > /start.sh

RUN chmod +x /start.sh

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["/start.sh"]

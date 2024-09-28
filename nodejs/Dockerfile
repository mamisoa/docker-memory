# Base image
FROM node:lts-bullseye-slim

# Install SSH server and other necessary packages
RUN apt-get update && apt-get install -y openssh-server curl && rm -rf /var/lib/apt/lists/*

# Create directory for ssh keys
RUN mkdir /var/run/sshd

# SSH configuration
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of your app's source code
COPY . .

# Create a script to start services
RUN echo '#!/bin/bash\n\
mkdir -p /root/.ssh\n\
touch /root/.ssh/authorized_keys\n\
chmod 700 /root/.ssh\n\
chmod 600 /root/.ssh/authorized_keys\n\
\n\
# Add all SSH_PUBLIC_KEY_* to authorized_keys\n\
for var in $(compgen -A variable | grep ^SSH_PUBLIC_KEY_); do\n\
    echo "${!var}" | tr -d '\r' >> /root/.ssh/authorized_keys\n\
done\n\
\n\
service ssh start\n\
\n\
# Debug: List contents of /app\n\
echo "Contents of /app:"\n\
ls -la /app\n\
echo "Contents of /app/node_modules:"\n\
ls -la /app/node_modules\n\
\n\
# Start the Node.js application\n\
node index.js\n\
' > /start.sh

RUN chmod +x /start.sh

# Expose the port your app runs on
EXPOSE 3000

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Start the services
CMD ["/start.sh"]

# Python base image use kar rahe hain
FROM python:3.10-slim

# Bun install karne ke liye zaroori tools daal rahe hain
RUN apt-get update && apt-get install -y curl unzip && rm -rf /var/lib/apt/lists/*

# Bun install kar rahe hain
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

WORKDIR /app

# 1. Python Bot ke packages install karo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Bun API ke packages install karo
COPY package.json bun.lockb* ./
RUN bun install --production

# 3. Saara code copy karo (Bot aur API dono ki files ek hi folder me honi chahiye)
COPY . .

# 4. Ek bash script banao jo API aur Bot dono ko ek sath start kare
RUN echo '#!/bin/bash\n\
bun start & \n\
python bot.py\n\
wait -n\n\
' > start.sh && chmod +x start.sh

# Ports expose kar do
EXPOSE 5000
EXPOSE 8080

# Script ko run kar do
CMD ["./start.sh"]

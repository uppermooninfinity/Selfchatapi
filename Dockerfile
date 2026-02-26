# Base Python image (slim)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Upgrade pip and install dependencies
RUN python3 -m pip install --upgrade pip setuptools
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

# Run your Telegram bot
CMD ["python3", "-m", "main"]

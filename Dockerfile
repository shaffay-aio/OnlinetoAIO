# Use the official lightweight Python image.
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the app code
COPY . /app
WORKDIR /app

# Expose a default port
EXPOSE 8027

# Use environment variable for the port, defaulting to 8027 if not set
CMD ["streamlit", "run", "app.py", "--server.port=8027"]
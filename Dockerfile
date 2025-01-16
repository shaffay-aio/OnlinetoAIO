# STEP-1 : official lightweight python base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# STEP-2 : Copy & Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# STEP-3 : Copy the app code
COPY . /app
WORKDIR /app

# STEP-4 : Expose port
EXPOSE 8027

# STEP-5: application running command
CMD ["streamlit", "run", "app.py", "--server.port=8027"]
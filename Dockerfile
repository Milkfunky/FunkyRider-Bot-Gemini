# Base image for Python applications
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Define the port that the application will listen on
# Cloud Run automatically sets the PORT environment variable
ENV PORT 8080

# Command to run the application when the container starts
# Use gunicorn for a production-ready WSGI server
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
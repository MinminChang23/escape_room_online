# Use the official Python 3.10 image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application
COPY . .

# Command to run your app (adjust as needed)
CMD ["python", "main.py"]

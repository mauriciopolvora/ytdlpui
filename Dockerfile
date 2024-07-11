# Use the official Python 3.11 image as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY . .

EXPOSE 5000

# Set the entry point for the container
CMD [ "flask", "run" ]
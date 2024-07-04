# Use an official Python runtime as a parent image with ARM support
FROM --platform=linux/arm64 python:3.12.0

# Set the working directory in the container
WORKDIR /app

# Copy the current directory into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run app.py when the container launches
CMD ["python", "-u", "./main.py"]

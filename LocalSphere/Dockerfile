# Use an official Python runtime as the base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . /app/

# Expose port 8000 for the Django app
EXPOSE 8000

# Set the entrypoint for the container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
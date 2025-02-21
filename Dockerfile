# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install Node.js and npm (required for Tailwind CSS CLI)
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Install npm dependencies
COPY package.json /code/
RUN npm install

# Copy project
COPY . /code/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["sh", "-c", "npm run build & python manage.py runserver 0.0.0.0:8000"]
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y curl

# Install Node.js and npm (for Tailwind CSS CLI)
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Install npm dependencies
COPY package.json package-lock.json /code/
RUN npm install

# Copy project files AFTER dependencies (for better caching)
COPY . /code/

# Expose the port Django runs on
EXPOSE 8000

# Ensure Tailwind is built before starting Django
CMD npm run build && python manage.py runserver 0.0.0.0:8000

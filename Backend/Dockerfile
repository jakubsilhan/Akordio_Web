# syntax=docker/dockerfile:1

# Setup environment
FROM python:3.11-slim

# Setup workdir
WORKDIR /backend

# Copy requirements and install dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy all
COPY . .

# Run via gunicorn with 4 workers
CMD ["gunicorn", "-w", "4", "run:app", "-b", "0.0.0.0:5000"]
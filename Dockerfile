# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the working directory explicitly
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
# Increased timeout and added retries for better network robustness
RUN pip install --no-cache-dir -r requirements.txt --default-timeout=120 --retries 5

# Copy the entire application code into the working directory
COPY . .

# Expose the port that Flask runs on
EXPOSE 5000

# Define environment variable for Flask application
ENV FLASK_APP=app.py

# Command to run the Flask application using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
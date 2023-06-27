# Use an official Python runtime as the base image
FROM python:3.9-slim

# Copy local code to the container image.
# ENV APP_HOME /app
# WORKDIR $APP_HOME
# COPY . ./
WORKDIR /app
# Copy the requirements file and install the dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# # Copy the application code into the container
# COPY app/ ./app/
# Copy the application code into the container
COPY . .

EXPOSE 8000


# Set the command to run the API server
# CMD /usr/bin/uvicorn app.main:app --host 0.0.0.0 --port $PORT
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", $PORT]

# Use an official Python runtime as the base image
FROM python:3.9

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Copy the requirements file and install the dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY app/ ./app/

# Set the command to run the API server
# CMD /usr/bin/uvicorn app.main:app --host 0.0.0.0 --port $PORT
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", $PORT]

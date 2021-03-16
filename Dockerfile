# This file is a template, and might need editing before it works on your project.
# is the base image your Docker image will be built upon. This will be pulled from DockerHub.
FROM python:3.8

# ensures that the output Django writes to the terminal comes out in real time without being buffered somewhere. 
# This makes your Docker logs useful and complete.
ENV PYTHONUNBUFFERED 1

# Edit with mysql-client, postgresql-client, sqlite3, etc. for your needs.
# Or delete entirely if not needed.
RUN apt-get update
RUN apt-get install -y libmysqlclient-dev

# creates a new folder in your container called app which will be your project’s root inside the container
WORKDIR /app

# OPY requirements.txt /app/requirements.txt copies your local requirements.txt file to the Docker container.
COPY requirements.txt /app/requirements.txt
# RUN pip install -r requirements.txt will make sure you have all your project dependencies installed inside the container.
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install mysqlclient
# COPY . /app and finally it’s time to copy your project’s content into the Docker container.
COPY . /app

# For Django
# EXPOSE 8000
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# For some other command
# CMD ["python", "app.py"]

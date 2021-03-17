# python
FROM python:3.8
ENV PYTHONUNBUFFERED 1

# Edit with mysql-client, postgresql-client, sqlite3, etc. for your needs.
# Or delete entirely if not needed.
RUN apt-get update
RUN apt-get install -y default-libmysqlclient-dev

# creates a new folder
WORKDIR /app

# COPY requirements.txt
COPY requirements.txt /app/requirements.txt

# RUN pip install -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install mysqlclient

# COPY . /app into the Docker container.
COPY . /app


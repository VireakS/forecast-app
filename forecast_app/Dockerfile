# Pull base image
FROM python:3.10


# Set work directory
WORKDIR /usr/src/app

# Install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# Copy project
COPY . /usr/src/app/
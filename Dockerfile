FROM python:3.9.6

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY . .
RUN pip install -r requirements.txt
RUN pip install -r fb_parser_get/requirements.txt

# copy project

COPY .  .
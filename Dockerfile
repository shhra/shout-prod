# pull official base image
FROM python:3.6-alpine

# set environmnet variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /usr/src/shout

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/shout/requirements.txt
RUN pip3 install https://download.pytorch.org/whl/cpu/torch-1.0.1.post2-cp36-cp36m-linux_x86_64.whl
# install psycopg2
RUN pip3 install sentencepiece
RUN apk update \
    && apk add --virtual build-deps build-base gcc python3-dev musl-dev \
    && apk add gfortran libpng-dev openblas-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 numpy scipy\
    && apk del build-deps


RUN pip install --no-cache-dir -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/shout/entrypoint.sh

# copy project
COPY . /usr/src/shout/

# run entrypoint.sh
ENTRYPOINT ["/usr/src/shout/entrypoint.sh"]

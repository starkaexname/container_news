FROM python
RUN apt-get update -y
RUN apt-get upgrade -y
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY ./container ./container
CMD [ 'python3', './container/manage.py', 'runserver', '0.0.0.0:8000']
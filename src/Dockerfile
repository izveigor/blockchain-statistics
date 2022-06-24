FROM python:3.9
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY ./entrypoint.sh .
RUN chmod +x ./entrypoint.sh

COPY . .
RUN mv static status

ENTRYPOINT ["bash", "./entrypoint.sh"]
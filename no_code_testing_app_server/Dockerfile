FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY ./ /app

WORKDIR /app

COPY ./entry-point.sh /

EXPOSE 8000

ENTRYPOINT ["sh","/entry-point.sh"]

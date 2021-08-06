FROM python:3.7-slim-stretch
MAINTAINER Transferwise

COPY ./ /app
WORKDIR /app

RUN pip install .

EXPOSE 5000

ENTRYPOINT ["cfexpose", "parallel"]

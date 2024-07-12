FROM python:3.12-slim-stretch
MAINTAINER Wise

COPY ./ /app
WORKDIR /app

RUN pip install .

EXPOSE 5000

ENTRYPOINT ["cfexpose", "export"]

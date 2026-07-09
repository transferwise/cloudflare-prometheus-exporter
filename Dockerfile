FROM tw-base-python.arti.tw.ee/tw-base-python:3.12
LABEL "MAINTAINER"="Wise"

COPY ./ /app
WORKDIR /app

# tw-base-python runs as non-root (UID 65534). pip install writes into
# system site-packages, which requires root, so switch to root for the install.
USER 0
RUN pip install . && chown -R 65534:65534 /app

EXPOSE 5000

# Drop back to the non-root user before running the entrypoint.
USER 65534
ENTRYPOINT ["cfexpose", "export"]

FROM mcr.microsoft.com/playwright:v1.50.0-noble
WORKDIR /app
RUN --mount=type=bind,source=.,target=/app,rw \
    apt update && \
    apt install python3 python3-setuptools -y && \
    mkdir /tmp/output-folder && \
    python3 /app/setup.py install
ENTRYPOINT [ "python3", "-m", "find404crawler", "--output-folder", "/tmp/output-folder" ]

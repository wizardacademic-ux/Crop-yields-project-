# Base image: python:3.11-slim-trixie, pinned by digest (resolved from
# hub.docker.com, linux/amd64).
FROM python:3.11-slim-trixie@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534

RUN pip install --no-cache-dir pandas==2.2.2 openpyxl==3.1.2

WORKDIR /workspace
COPY data/ /workspace/environment/data/

CMD ["/bin/bash"]

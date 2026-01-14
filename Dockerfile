FROM rasa/rasa-sdk:2.8.3

USER root

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y build-essential cmake && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir llama-cpp-python psutil

USER 1001
FROM debian:jessie

RUN deps='python python-pip stow ca-certificates'; \
    set -x; \
    apt-get update && \
    apt-get install -y --no-install-recommends $deps && \
    pip install click && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

CMD ["/bin/bash"]

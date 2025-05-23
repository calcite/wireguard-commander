FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye
RUN git config --add devcontainers-theme.show-dirty 1 &&\
    echo "alias ll='ls -la'" >> /etc/bash.bashrc
RUN pip install pdm && \
    pdm config python.use_venv False
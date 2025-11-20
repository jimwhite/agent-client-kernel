FROM quay.io/jupyter/minimal-notebook:latest

USER root
RUN apt-get update && apt-get install -y \
    graphviz \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

USER jovyan

# Install Kimi CLI using pip
RUN pip install --upgrade pip \
    && pip install kimi-cli

COPY --chown=jovyan:users ../.. /home/jovyan/agent-client-kernel

WORKDIR /home/jovyan

RUN cd /home/jovyan/agent-client-kernel \
    && pip install --upgrade uv jupyter-mcp-tools \
    && git submodule update --init --recursive \
    && pip install -e . \
    && python -m agentclientkernel install --user

FROM quay.io/jupyter/minimal-notebook:latest

USER root
RUN apt-get update && apt-get install -y \
    graphviz \
    git \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

USER jovyan

# Install uv and use it to install Kimi CLI (recommended method)
RUN pip install --upgrade pip uv && \
    uv tool install --python 3.13 kimi-cli

COPY --chown=jovyan:users ../.. /home/jovyan/agent-client-kernel

WORKDIR /home/jovyan

# Clone the metakernel submodule since .git directory is not copied
RUN cd /home/jovyan/agent-client-kernel \
    && git clone -b ipykernel7 https://github.com/jimwhite/metakernel.git metakernel

RUN cd /home/jovyan/agent-client-kernel \
    && pip install --upgrade pip \
    && pip install --upgrade uv jupyter-mcp-tools \
    && pip install -e . \
    && python -m agentclientkernel install --user

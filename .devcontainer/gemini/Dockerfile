FROM quay.io/jupyter/minimal-notebook:latest

USER root
RUN apt-get update && sudo apt-get install -y \
    nodejs npm \
    graphviz \
    python3 \
    make \
    g++ \
    curl \
    git \
    ca-certificates

# Install Gemini CLI from npm
RUN npm install -g @google/gemini-cli --unsafe-perm

USER jovyan

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

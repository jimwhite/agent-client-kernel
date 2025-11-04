FROM quay.io/jupyter/minimal-notebook:latest

USER root
RUN apt-get update && sudo apt-get install -y \
    nodejs npm \
    graphviz

# Install npm packages
RUN npm install -g @openai/codex @zed-industries/codex-acp

USER jovyan

COPY --chown=jovyan:users . /home/jovyan/agent-client-kernel

WORKDIR /home/jovyan

RUN cd /home/jovyan/agent-client-kernel \
    && git submodule update --init --recursive \
    && pip install -e . \
    && python -m agentclientkernel install --user

FROM quay.io/jupyter/minimal-notebook:latest

USER root
RUN apt-get update && sudo apt-get install -y \
    nodejs npm \
    graphviz

# Install npm packages
RUN npm install -g @openai/codex@latest @zed-industries/codex-acp@latest

USER jovyan

COPY --chown=jovyan:users . /home/jovyan/agent-client-kernel

WORKDIR /home/jovyan

RUN cd /home/jovyan/agent-client-kernel \
    && conda install uv \
    && git submodule update --init --recursive \
    && uv sync --locked --all-extras --dev \
    && uv pip install -e . \
    && uv pip install jupyter-mcp-tools 
    # && uv run python -m agent_client_kernel install --user

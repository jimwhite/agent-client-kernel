FROM quay.io/jupyter/minimal-notebook:latest

USER root

# Install Go and build dependencies
RUN apt-get update && apt-get install -y \
    wget \
    git \
    graphviz \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Go as root
RUN wget https://go.dev/dl/go1.23.4.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go1.23.4.linux-amd64.tar.gz \
    && rm go1.23.4.linux-amd64.tar.gz

ENV PATH="/usr/local/go/bin:${PATH}"

USER jovyan

# Clone and build cagent
RUN git clone https://github.com/docker/cagent.git /tmp/cagent \
    && cd /tmp/cagent \
    && go build -o cagent . \
    && mkdir -p /home/jovyan/.local/bin \
    && cp cagent /home/jovyan/.local/bin/ \
    && rm -rf /tmp/cagent

ENV PATH="/home/jovyan/.local/bin:${PATH}"

COPY --chown=jovyan:users ../.. /home/jovyan/agent-client-kernel

WORKDIR /home/jovyan

RUN cd /home/jovyan/agent-client-kernel \
    && pip install --upgrade pip \
    && pip install --upgrade uv jupyter-mcp-tools \
    && git submodule update --init --recursive \
    && pip install -e . \
    && python -m agentclientkernel install --user

FROM quay.io/jupyter/minimal-notebook:latest

USER root

# Install Rust and build dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    pkg-config \
    libssl-dev \
    libdbus-1-dev \
    protobuf-compiler \
    libprotobuf-dev \
    ca-certificates \
    git \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Install Rust as jovyan user
USER jovyan
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/home/jovyan/.cargo/bin:${PATH}"

# Clone and build Goose
RUN git clone https://github.com/block/goose.git /tmp/goose \
    && cd /tmp/goose \
    && cargo build --release --package goose-cli \
    && mkdir -p /home/jovyan/.local/bin \
    && cp target/release/goose /home/jovyan/.local/bin/ \
    && rm -rf /tmp/goose

ENV PATH="/home/jovyan/.local/bin:${PATH}"

COPY --chown=jovyan:users ../.. /home/jovyan/agent-client-kernel

WORKDIR /home/jovyan

RUN cd /home/jovyan/agent-client-kernel \
    && pip install --upgrade pip \
    && pip install --upgrade uv jupyter-mcp-tools \
    && git submodule update --init --recursive \
    && pip install -e . \
    && python -m agentclientkernel install --user

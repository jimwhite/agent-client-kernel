FROM ghcr.io/jimwhite/acl2-jupyter:latest

USER root
RUN apt-get update && sudo apt-get install -y \
    nodejs npm \
    graphviz

# Install npm packages
RUN npm install -g @openai/codex @zed-industries/codex-acp

USER jovyan

FROM python:3.13.0-bookworm

ENV HOME="/root"

# Install pulseaudio
RUN apt-get update
RUN apt-get install pulseaudio -y

# Install rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
# Expose cargo to PATH
ENV PATH="$PATH:/$HOME/.cargo/bin"

# Install rye
ENV RYE_HOME="/opt/rye"
RUN curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" bash
# Expose rye to PATH
ENV PATH="$PATH:$RYE_HOME/shims"

# Set current working directory
WORKDIR /opt/termnautica

# Copy project source (See `.dockerignore`)
COPY ./ ./

# Sync and run
RUN rye sync
CMD ["rye", "run", "termnautica"]


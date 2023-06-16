FROM python:3.11.4-bullseye

# Install system things.
RUN set -e && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        supervisor \
    && \
    rm -rf /var/lib/apt/lists/*

# Do everthing in /app.
WORKDIR /app

# System-level dependencies.
RUN set -e && \
    useradd --create-home python

# Change to non-root user, which is called python in this app. Because it has
# the same uid and guid as the default linux user (and macos enforces this
# too), it avoids permissions issues with docker writing to mounted volumes.
USER python

# Env.
ENV PYTHONUNBUFFERED="true" \
    PYTHONPATH="." \
    PATH="${PATH}:/home/python/.local/bin" \
    USER="python" \
    CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Install python dependencies.
COPY --chown=python:python requirements.txt ./
RUN pip install --user --no-cache-dir --disable-pip-version-check -r requirements.txt

# Add everything.
COPY --chown=python:python . /app

# Run/
EXPOSE 5123
CMD ["sh", "/app/run.sh"]


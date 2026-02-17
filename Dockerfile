FROM ghcr.io/berriai/litellm:main-stable

WORKDIR /app

COPY litellm_hooks.py /app/litellm_hooks.py
COPY config.yaml /app/config.yaml

ENV PYTHONPATH=/app

CMD ["--config", "/app/config.yaml", "--port", "4000"]

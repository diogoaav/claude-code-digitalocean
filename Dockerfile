FROM ghcr.io/berriai/litellm:main-stable

COPY litellm_hooks.py /app/litellm_hooks.py
COPY config.yaml /app/config.yaml

CMD ["--config", "/app/config.yaml", "--port", "4000"]

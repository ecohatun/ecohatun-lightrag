FROM ghcr.io/vectorize-io/hindsight@sha256:bb117258681a4a44289bc042185a16d2bb0b30d4a94adcd0dc799d445794f0cb
COPY vendor/hindsight_ext_static_keys_tenant /app/extensions/hindsight_ext_static_keys_tenant
ENV PYTHONPATH=/app/extensions
RUN /app/api/.venv/bin/python -c "import hindsight_ext_static_keys_tenant"

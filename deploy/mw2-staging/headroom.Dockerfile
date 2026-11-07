ARG PYTHON_IMAGE
FROM ${PYTHON_IMAGE}
RUN pip install --no-cache-dir "headroom-ai[proxy]==0.43.1" \
    && mkdir -p /data/cache /app \
    && chown -R 10001:10001 /data /app
COPY headroom_entrypoint.py /app/headroom_entrypoint.py
USER 10001:10001
WORKDIR /app
ENTRYPOINT ["python", "/app/headroom_entrypoint.py"]

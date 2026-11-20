# Imagen para ejecutar pre-commit en Linux desde Windows (evita que el Control de
# aplicaciones de Windows bloquee los ejecutables que pre-commit descarga).
FROM python:3.14-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir "pre-commit==4.*" \
    && git config --system --add safe.directory '*'
ENV PRE_COMMIT_HOME=/cache
WORKDIR /src
ENTRYPOINT ["pre-commit"]

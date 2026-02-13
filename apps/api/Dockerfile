# Build context: apps/api
# Requires conda-linux-64.lock (generate with: conda-lock -k explicit -p linux-64 -f env.yaml)
FROM mambaorg/micromamba:2.5.0

WORKDIR /app

# Copy lockfile first for better Docker layer caching (reproducible install)
COPY --chown=$MAMBA_USER:$MAMBA_USER conda-linux-64.lock /tmp/env.lock
RUN micromamba install -y -n base -f /tmp/env.lock && \
    micromamba clean --all --yes

# Copy application code
COPY --chown=$MAMBA_USER:$MAMBA_USER . /app

EXPOSE 8000

# micromamba image ENTRYPOINT activates base env; do not override it
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

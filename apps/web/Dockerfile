# Build context: repo root (dockerfile: apps/web/Dockerfile)
FROM node:24-alpine AS base

# Install pnpm and su-exec (for entrypoint privilege drop)
RUN apk add --no-cache su-exec \
  && corepack enable \
  && corepack prepare pnpm@10.0.0 --activate
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

WORKDIR /app

# Copy workspace root and web app for install
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY apps/web apps/web

# Install with frozen lockfile (reproducible)
RUN pnpm install --frozen-lockfile

# Install entrypoint that fixes volume ownership and drops to `node` user
COPY apps/web/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 5173

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Install on start when volume overwrites files; then run dev
CMD ["sh", "-c", "pnpm install --frozen-lockfile && pnpm --filter web dev --host 0.0.0.0"]

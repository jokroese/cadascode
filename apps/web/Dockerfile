# Build context: repo root (dockerfile: apps/web/Dockerfile)
FROM node:24-alpine AS base

# Install pnpm
RUN corepack enable && corepack prepare pnpm@10.0.0 --activate
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

WORKDIR /app

# Copy workspace root and web app for install
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY apps/web apps/web

# Install with frozen lockfile (reproducible)
RUN pnpm install --frozen-lockfile

EXPOSE 5173

# Install on start when volume overwrites files; then run dev
CMD ["sh", "-c", "pnpm install --frozen-lockfile && pnpm --filter web dev --host 0.0.0.0"]

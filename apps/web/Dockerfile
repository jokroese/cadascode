FROM node:24-alpine AS base

# Needed to drop from root -> node after fixing volume ownership
RUN apk add --no-cache su-exec

# Install pnpm
RUN corepack enable && corepack prepare pnpm@10.0.0 --activate
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

WORKDIR /app

# Copy workspace root and web app for install
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY apps/web apps/web

RUN pnpm install --frozen-lockfile

# Entry point for dev volume ownership initialisation
COPY apps/web/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 5173

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["sh", "-c", "pnpm install --frozen-lockfile && pnpm --filter web dev --host 0.0.0.0"]
# Bun is the default package manager for this project (see package.json
# "packageManager" field). Pinned to the latest bun release.
FROM oven/bun:1.3.14

WORKDIR /app

COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile

COPY . .
ENV NEXT_TELEMETRY_DISABLED=1

# `bun https` runs `next dev --experimental-https` (see package.json) with the
# self-signed certs in security_keys/, serving HTTPS on port 3000.
EXPOSE 3000

CMD ["bun", "https"]

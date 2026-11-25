# Demo image: Ganache (embedded chain), the deployed contract and the app in one container.
# State is in memory and on the container disk, so a restart gives a clean demo.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm curl \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt package.json package-lock.json ./
RUN pip install --no-cache-dir -r requirements.txt && npm ci --omit=dev
# Fetch the Solidity compiler at build time so startup needs no network.
RUN python -c "from solcx import install_solc; install_solc('0.8.19')"
COPY . .
ENV PASSAGE_DEMO=1 PORT=8000
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s CMD curl -sf http://127.0.0.1:${PORT}/ || exit 1
CMD ["sh", "-c", "python main.py --host 0.0.0.0 --port ${PORT}"]

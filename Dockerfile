FROM ghcr.io/astral-sh/uv:python3.14-alpine

WORKDIR /app
VOLUME /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "python", "main.py"]
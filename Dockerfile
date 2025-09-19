FROM python:3.11-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential curl netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser
WORKDIR /app

COPY pyproject.toml .

RUN pip install --upgrade pip \
 && python - <<'PY'
import tomllib
from pathlib import Path
d = tomllib.loads(Path('pyproject.toml').read_text())
deps = d.get('project', {}).get('dependencies', [])
Path('deps.txt').write_text('\n'.join(deps))
PY

RUN pip install --no-cache-dir -r deps.txt

COPY . .


RUN mkdir -p /app/run && chown -R appuser:appuser /app
RUN chmod +x /app/entrypoint.sh

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

ENTRYPOINT ["/app/entrypoint.sh"]

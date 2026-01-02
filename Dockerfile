FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 先装依赖（requirements 在 langame/ 里）
COPY langame/requirements.txt /app/langame/requirements.txt
RUN pip install --no-cache-dir -r /app/langame/requirements.txt

# 再复制代码
COPY . /app

# 关键：运行时根目录切到 manage.py 那层
WORKDIR /app/langame

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "langame.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "60"]

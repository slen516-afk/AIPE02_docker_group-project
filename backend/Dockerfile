FROM python:3.11.14-slim

LABEL maintainer="tz"

# 設置系統環境變數
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN mkdir -p /app/import_data

# 安裝套件
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼（開發模式下會被 compose 的 volume 覆蓋）
COPY . .

CMD ["python", "main.py"]

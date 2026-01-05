# 1. 統一 Python 版本
FROM python:3.11.14-slim

LABEL maintainer="tz-frontend"

# 2. 保留系統環境變數設定
# PYTHONDONTWRITEBYTECODE 防止產生 .pyc 檔（保持容器乾淨）
# PYTHONUNBUFFERED 確保 Log 能即時印出，方便你在 Docker 看到 Flask 的報錯
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \ 
    BACKEND_URL=http://backend:8000

WORKDIR /app

# 3. 系統套件（前端主要需要 curl 用於測試，其餘可視情況保留）
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. 安裝依賴 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 複製程式碼 (包含你的 Frontend/ 資料夾)
COPY . .

# 6. 告知埠號
EXPOSE 3000

# 7. 啟動指令 
# 這裡要改成 python app.py 
CMD ["python", "app_frontend.py"]

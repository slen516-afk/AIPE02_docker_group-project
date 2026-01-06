FROM node:20-slim

LABEL maintainer="tz"

WORKDIR /app

# 若後續有增加 package.json 需求
# COPY package.json* ./
RUN npm install -g live-server

COPY . .

# 開發時使用 live-server 達成 Hot Reload
CMD ["live-server", "--port=3000", "--host=0.0.0.0"]

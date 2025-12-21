# iSpan_AIPE02_T1_docker-project
Team1_docker-project
本專案使用 Docker 容器化技術，支援 VS Code Dev Containers 直接開發

## 環境準備
- 確保Ubuntu 24.04包含以下工具:
	- Git, Docker, Docker-compose
	- VS Code (需安裝套件: Dev Containers)

## 快速上手
### 複製專案
- git clone 倉庫網址
- cd iSpan_AIPE02_T1_docker-project
- cp .env.example .env

### 啟用container
- docker-compose up -d

### 維護套件清單
- 如有增減套件請更新至requirements.txt
- git add
- git commit
- git push

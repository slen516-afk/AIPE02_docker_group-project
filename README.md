#使用前請先記得清掉舊的容器
#使.env required=flase,docker不需要每次啟動都要讀取github不能上傳的.env檔案
#pull下來以後請記得複製一份.env.example並改名為.env才可進入容器

# iSpan_AIPE02_T1_docker-project
Team1_docker-project
本專案使用 Docker 容器化技術，支援 VS Code Dev Containers 直接開發

## 環境準備
- 作業系統: Ubuntu 24.04(建議使用 WSL2 + Windows 10/11 或原生 Ubuntu)
	- 	WSL2 特別說明：
		建議使用 Ubuntu 24.04 作為 WSL2 發行版
		Docker Desktop 需啟用 WSL2 後端
		VS Code 需安裝 Remote - WSL 套件
- 必備工具:
	- Git
 	- Docker(包含 Docker-compose)
	- VS Code (需安裝套件: Dev Containers)

## 快速上手
### 初次啟動
[開啟桌面 Docker] 
        │
        ▼
[Git Clone 專案]
        │
        ▼
[進入專案目錄]
        │
        ▼
[複製環境變數範例]
        │
        └─> cp .env.example .env
        │
        ▼
[VS Code: Dev Containers → Reopen in Container]
        │
        ├─> 選擇 db container (MySQL)
        │       └─> 容器啟動 → MySQL 可用
        │
        ├─> 選擇 be container (Python/Flask)
        │       └─> 容器啟動 → Flask server 可用
        │
        └─> 選擇 fe container (前端)
                └─> 容器啟動 → 靜態頁面可訪問後端

### 再次啟用
[開啟桌面 Docker] 
        │
        ▼
[進入專案目錄]
        │
        ▼
[VS Code: Dev Containers → Reopen in Container]
        │
        ├─> 選擇 db container
        │       └─> 已存在容器 → 直接啟動 MySQL
        │
        ├─> 選擇 be container
        │       └─> 已存在容器 → Flask server 啟動
        │
        └─> 選擇 fe container
                └─> 已存在容器 → 前端頁面可訪問

### 套件與版本維護
- Python 後端：
	- requirements.txt
	- 如新增或刪除套件，請同步更新 requirements.txt：
		pip freeze > requirements.txt
		git add requirements.txt
		git commit -m "Update dependencies"
		git push

### 注意事項
- 容器切換：依照工作角色選擇對應的 devcontainer。
- Volume 掛載：devcontainer 會掛載本地程式碼，修改即時反映於容器內。
- WSL2 特別注意：
	- Docker Desktop 需啟用 WSL2 後端
	-確認 Ubuntu WSL2 版本 ≥ 24.04

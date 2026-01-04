import os
import uvicorn
import pandas as pd
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

app = FastAPI()


def get_db_engine():
    # 你的資料庫連線設定 (Docker 內部連線)
    db_config = {
        "host": "db",  # 服務名稱 (對應 docker-compose)
        "port": 3306,
        "user": "admin",  # 根據你的設定
        "password": "password",  # 根據你的設定
        "db": "project_db",
        "charset": "utf8mb4",
    }

    url = URL.create(
        drivername="mysql+pymysql",
        username=db_config["user"],
        password=db_config["password"],
        host=db_config["host"],
        port=db_config["port"],
        database=db_config["db"],
        query={"charset": db_config["charset"]},
    )

    return create_engine(url)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend is running!"}


@app.get("/api/analysis")
def get_analysis():
    engine = get_db_engine()
    try:
        # --- 修改：先用最簡單的查詢測試連線 ---
        # 因為你的 DBeaver 截圖顯示欄位是 title, telecommuting...
        # 原本的查詢可能會因為找不到 country 欄位而報錯
        sql = "SELECT * FROM temp_raw_data LIMIT 5;"

        # 讀取資料
        df = pd.read_sql_query(sql, engine)

        # 回傳結果
        return {"data": df.to_dict(orient="records")}

    except Exception as e:
        return {"error": str(e)}
    finally:
        engine.dispose()


if __name__ == "__main__":
    print("啟動 Web Server (Port 8001)...")
    # 修改：改用 8001 避開原本被佔用的 8000
    uvicorn.run(app, host="0.0.0.0", port=8001)

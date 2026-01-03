import os
import uvicorn
import pandas as pd
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

app = FastAPI()


# 這是你原本的資料庫連線邏輯，包裝成函式
def get_db_engine():
    # 從環境變數讀取設定 (Docker 最佳實踐)
    db_config = {
        "host": os.getenv("DB_HOST", "db"),
        "user": os.getenv("DB_USER", "admin"),
        "password": os.getenv("DB_PASSWORD", "password"),
        "database": os.getenv("DB_NAME", "project_db"),
        "port": int(os.getenv("DB_PORT", 3306)),
        "charset": "utf8mb4",
    }

    url = URL.create(
        drivername="mysql+pymysql",
        username=db_config["user"],
        password=db_config["password"],
        host=db_config["host"],
        port=db_config["port"],
        database=db_config["database"],
        query={"charset": db_config["charset"]},
    )

    return create_engine(url, pool_pre_ping=True)


# --- 這裡開始是 API 設定 ---


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend is running!"}


@app.get("/api/analysis")
def get_analysis():
    """
    這個 API 會回傳你原本印出來的那些 DataFrame 資料
    """
    engine = get_db_engine()
    try:
        # 這裡放入你原本的 SQL 查詢
        sql_country = """
        SELECT country, 
               SUM(CASE WHEN fraudulent = 0 THEN 1 ELSE 0 END) AS legitimate,
               SUM(CASE WHEN fraudulent = 1 THEN 1 ELSE 0 END) AS fraudulent,
               COUNT(*) AS total
        FROM temp_raw_data 
        WHERE country IS NOT NULL AND country != 'Unknown'
        GROUP BY country
        ORDER BY total DESC 
        LIMIT 10;
        """

        # 讀取資料
        df_country = pd.read_sql_query(sql_country, engine)

        # 轉成字典格式回傳給前端 (JSON)
        return {"country_analysis": df_country.to_dict(orient="records")}

    except Exception as e:
        return {"error": str(e)}
    finally:
        engine.dispose()


# --- 啟動點 ---
if __name__ == "__main__":
    # 這行是關鍵！它會讓程式「卡住」並一直監聽 8000 port
    print("啟動 Web Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

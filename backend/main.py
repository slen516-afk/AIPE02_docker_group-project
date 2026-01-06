import os
import uvicorn
import pandas as pd
import pymysql
# from fastapi import FastAPI
from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# app = FastAPI()
app = Flask(__name__)

# 資料庫連線設定
def get_db_engine():
    db_config = {
        "host": "db",  
        "port": 3306,
        "user": "admin",  
        "password": "password",  
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

    engine = create_engine(
        url,
        pool_pre_ping=True,  # 避免連線閒置被 MySQL 斷線
        future=True,
    )
    return engine

# 取得資料庫資料 ->哲廣段落打包成function
def fetch_recruitment_data(engine):
    # 1. 每個國家自己的合法與虛假招募
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
    # 2. 是否遠距、有無公司標誌各自合法及虛假招募
    sql_features = """
    SELECT 
        SUM(CASE WHEN telecommuting = 1 AND fraudulent = 0 THEN 1 ELSE 0 END) as tele_legit,
        SUM(CASE WHEN telecommuting = 1 AND fraudulent = 1 THEN 1 ELSE 0 END) as tele_fraud,
        SUM(CASE WHEN telecommuting = 0 AND fraudulent = 0 THEN 1 ELSE 0 END) as office_legit,
        SUM(CASE WHEN telecommuting = 0 AND fraudulent = 1 THEN 1 ELSE 0 END) as office_fraud,
        SUM(CASE WHEN has_company_logo = 1 AND fraudulent = 0 THEN 1 ELSE 0 END) as logo_legit,
        SUM(CASE WHEN has_company_logo = 1 AND fraudulent = 1 THEN 1 ELSE 0 END) as logo_fraud,
        SUM(CASE WHEN has_company_logo = 0 AND fraudulent = 0 THEN 1 ELSE 0 END) as no_logo_legit,
        SUM(CASE WHEN has_company_logo = 0 AND fraudulent = 1 THEN 1 ELSE 0 END) as no_logo_fraud
    FROM temp_raw_data;
    """

    # 3. 學歷、產業在合法與在虛假之間的關係
    sql_edu_ind = """
    SELECT edu_level, industry_group, 
           SUM(CASE WHEN fraudulent = 0 THEN 1 ELSE 0 END) AS legitimate_count,
           SUM(CASE WHEN fraudulent = 1 THEN 1 ELSE 0 END) AS fraudulent_count
    FROM temp_raw_data 
    WHERE edu_level != 'Unknown' AND industry_group != 'Unknown'
    GROUP BY edu_level, industry_group;
    """

    # 4. 就業類型在合法與虛假招募資料比例
    sql_emp_type = """
    SELECT employment_type, 
           SUM(CASE WHEN fraudulent = 0 THEN 1 ELSE 0 END) AS legitimate,
           SUM(CASE WHEN fraudulent = 1 THEN 1 ELSE 0 END) AS fraudulent
    FROM temp_raw_data 
    WHERE employment_type != 'Unknown'
    GROUP BY employment_type;
    """

    # 5. 虛假招募資料裡前五名高的產業別
    sql_top_industries = """
    SELECT industry_group, COUNT(*) as fraud_count 
    FROM temp_raw_data 
    WHERE fraudulent = 1 AND industry_group != 'Unknown'
    GROUP BY industry_group 
    ORDER BY fraud_count DESC 
    LIMIT 5;
    """
    
    return {
        "country": pd.read_sql_query(sql_country, engine),
        "features": pd.read_sql_query(sql_features, engine),
        "education_industry": pd.read_sql_query(sql_edu_ind, engine),
        "employment_type": pd.read_sql_query(sql_emp_type, engine),
        "top_industries": pd.read_sql_query(sql_top_industries, engine),
    }

# 數據轉換為輸出 ->雅茜段落打包為function
def build_analysis_result(dfs):
    return {
        "country": dfs["country"].to_dict(orient="columns"),
        "features": dfs["features"].iloc[0].to_dict(),
        "education_industry": dfs["education_industry"].to_dict(orient="columns"),
        "employment_type": dfs["employment_type"].to_dict(orient="columns"),
        "top_industries": dfs["top_industries"].to_dict(orient="columns"),
    }


# 建立路由供前端串接
@app.route("/")
def health_check():
    return jsonify({"status": "ok"})

# 取得分析資料API
@app.route("/api/analysis")
def get_analysis():
    engine = get_db_engine()
    try:
        # sql = "SELECT * FROM temp_raw_data LIMIT 5;"
        dfs = fetch_recruitment_data(engine)
        result = build_analysis_result(dfs)
        return jsonify({"data": result})

        # #讀取資料
        # df = pd.read_sql_query(sql, engine)

        # 回傳結果
        # return {"data": df.to_dict(orient="records")}

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        engine.dispose()


if __name__ == "__main__":
    print("啟動 Web Server (Port 8001)...")
    app.run(host="0.0.0.0", port=8001)

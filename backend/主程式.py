import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import pymysql  # 雖然 SQLAlchemy 會調用，但保留匯入可確保環境正確


def get_recruitment_analysis_data():
    # 1. 使用你在 Docker Compose 設定的參數
    db_config = {
        "host": "db",  # Docker 內部服務名稱
        "user": "admin",  # 你設定的 admin 帳號
        "password": "password",  # 你設定的密碼
        "database": "project_db",
        "port": 3306,  # 容器內部的 Port
        "charset": "utf8mb4",
    }

    # 2. 建立連線字串 (使用 mysql+pymysql 驅動)
    url = URL.create(
        drivername="mysql+pymysql",
        username=db_config["user"],
        password=db_config["password"],
        host=db_config["host"],
        port=db_config["port"],
        database=db_config["database"],
        query={"charset": db_config["charset"]},
    )

    # 建立 SQLAlchemy 引擎
    engine = create_engine(
        url,
        pool_pre_ping=True,
        future=True,
    )

    # --- SQL 語句區塊 ---
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

    sql_edu_ind = """
    SELECT edu_level, industry_group, 
           SUM(CASE WHEN fraudulent = 0 THEN 1 ELSE 0 END) AS legitimate_count,
           SUM(CASE WHEN fraudulent = 1 THEN 1 ELSE 0 END) AS fraudulent_count
    FROM temp_raw_data 
    WHERE edu_level != 'Unknown' AND industry_group != 'Unknown'
    GROUP BY edu_level, industry_group;
    """

    sql_emp_type = """
    SELECT employment_type, 
           SUM(CASE WHEN fraudulent = 0 THEN 1 ELSE 0 END) AS legitimate,
           SUM(CASE WHEN fraudulent = 1 THEN 1 ELSE 0 END) AS fraudulent
    FROM temp_raw_data 
    WHERE employment_type != 'Unknown'
    GROUP BY employment_type;
    """

    sql_top_industries = """
    SELECT industry_group, COUNT(*) as fraud_count 
    FROM temp_raw_data 
    WHERE fraudulent = 1 AND industry_group != 'Unknown'
    GROUP BY industry_group 
    ORDER BY fraud_count DESC 
    LIMIT 5;
    """

    try:
        # 使用 pandas 執行查詢
        df_country = pd.read_sql_query(sql_country, engine)
        df_features = pd.read_sql_query(sql_features, engine)
        df_edu_ind = pd.read_sql_query(sql_edu_ind, engine)
        df_emp_type = pd.read_sql_query(sql_emp_type, engine)
        df_top_industries = pd.read_sql_query(sql_top_industries, engine)

        print("資料讀取成功！")
        return df_country, df_features, df_edu_ind, df_emp_type, df_top_industries

    except Exception as e:
        print(f"資料庫連線或查詢出錯: {e}")
        return None, None, None, None, None

    finally:
        engine.dispose()


# --- 執行與測試 ---
if __name__ == "__main__":
    dfs = get_recruitment_analysis_data()
    df_country, df_features, df_edu_ind, df_emp_type, df_top_industries = dfs

    if df_country is not None:
        print("\n前十大國家招募分佈：")
        print(df_country.head())

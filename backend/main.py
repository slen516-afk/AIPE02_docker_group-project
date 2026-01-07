from __future__ import annotations  # 為了支援 Python 3.9 以下的型別提示

import os
from typing import Any, Dict, List, Tuple

import pandas as pd
import pycountry
from flask import Flask, jsonify
import pymysql

app = Flask(__name__)

# DB config from environment variables
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ["DB_NAME"]


# 國家兩碼代碼轉三碼代碼，失敗回傳 None
def _safe_iso2_to_iso3(code2: str) -> str | None:
    code2 = (code2 or "").strip().upper()
    if not code2 or code2 in {"UNSPECIFIED", "NAN", "NONE"}:
        return None
    try:
        country = pycountry.countries.get(alpha_2=code2)
        return country.alpha_3 if country else None
    except Exception:
        return None


# 依 ISO3 代碼取得英文國家名稱，失敗回傳原始代碼
def _country_name_en(iso3: str) -> str:
    try:
        c = pycountry.countries.get(alpha_3=iso3)
        return c.name if c else iso3
    except Exception:
        return iso3


# 建立MySQL連線
def _get_conn():

    return pymysql.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        autocommit=True,
        connect_timeout=10,
        read_timeout=30,
        write_timeout=30,
    )


# 把SQL查詢結果讀成DataFrame
def _q(sql: str, params: Dict[str, Any] | None = None) -> pd.DataFrame:
    with _get_conn() as conn:
        return pd.read_sql_query(sql, conn, params=params)


@app.get("/")
def home():
    return {"status": "ok", "message": "Backend is running!"}


@app.get("/health")
def health():
    try:
        _q("SELECT 1 AS ok")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.get("/api/data")
def api_data():

    df = _q(
        """
        SELECT
          title,
          telecommuting,
          has_company_logo,
          has_questions,
          employment_type,
          fraudulent,
          in_balanced_dataset,
          country,
          industry_group,
          edu_level
        FROM temp_raw_data
        """
    )

    # 若無資料，回傳空結構
    if df.empty:
        return jsonify(
            {
                "ranking": {"labels": [], "values": []},
                "charts": {
                    "section1": {"labels": [], "values": []},
                    "section2": {"labels": [], "values": []},
                    "section3": {"labels": [], "main": [], "sub": []},
                    "section4": {"labels": [], "values": []},
                    "section5": {"labels": [], "prodA": [], "prodB": []},
                    "section6": {
                        "labels": [],
                        "external": [],
                        "internal": [],
                        "other": [],
                    },
                    "section7": [],
                },
                "map": {},
                "map_names": {},
                "tables": {"table1": [], "table2": []},
            }
        )

    # 1) Ranking：虛假招募 (fraudulent=1) 前 5 名 title
    fraud_df = df[df["fraudulent"] == 1]
    top_titles = fraud_df["title"].fillna("Unknown").astype(str).value_counts().head(5)
    ranking_labels = [
        t[:40] + ("…" if len(t) > 40 else "") for t in top_titles.index.tolist()
    ]
    ranking_values = top_titles.values.tolist()

    # 2) Section1：圓餅圖 - 詐騙 vs 非詐騙
    fraud_counts = df["fraudulent"].value_counts().reindex([0, 1], fill_value=0)
    section1 = {
        "labels": ["非詐騙", "詐騙"],
        "values": [int(fraud_counts.loc[0]), int(fraud_counts.loc[1])],
    }

    # 3) Section2：折線圖 - employment_type 前 6 名筆數
    emp_counts = (
        df["employment_type"].fillna("Unknown").astype(str).value_counts().head(6)
    )
    section2 = {
        "labels": emp_counts.index.tolist(),
        "values": emp_counts.values.astype(int).tolist(),
    }

    # 4) Section3：區域圖 - 產業別(top 6) 的 詐騙 vs 非詐騙
    ind_top = (
        df["industry_group"]
        .fillna("Unknown")
        .astype(str)
        .value_counts()
        .head(6)
        .index.tolist()
    )
    sub_df = df[df["industry_group"].fillna("Unknown").astype(str).isin(ind_top)].copy()
    grp = (
        sub_df.groupby("industry_group")["fraudulent"]
        .value_counts()
        .unstack(fill_value=0)
    )
    grp = grp.reindex(ind_top)
    main = (
        grp.get(1, pd.Series([0] * len(ind_top), index=ind_top)).astype(int).tolist()
    )  # fraudulent
    sub = (
        grp.get(0, pd.Series([0] * len(ind_top), index=ind_top)).astype(int).tolist()
    )  # non
    section3 = {"labels": ind_top, "main": main, "sub": sub}

    # 5) Section4：雷達圖 - 特徵比例(%)
    def _ratio(col: str) -> float:
        try:
            return float(pd.to_numeric(df[col], errors="coerce").fillna(0).mean() * 100)
        except Exception:
            return 0.0

    section4 = {
        "labels": ["遠端", "有Logo", "有問題", "平衡資料", "詐騙"],
        "values": [
            round(_ratio("telecommuting"), 2),
            round(_ratio("has_company_logo"), 2),
            round(_ratio("has_questions"), 2),
            round(_ratio("in_balanced_dataset"), 2),
            round(_ratio("fraudulent"), 2),
        ],
    }

    # 6) Section5：分組直條圖 - 有Logo/無Logo 的 詐騙 vs 非詐騙
    logo = pd.to_numeric(df["has_company_logo"], errors="coerce").fillna(0).astype(int)
    fraud = pd.to_numeric(df["fraudulent"], errors="coerce").fillna(0).astype(int)
    with_logo_fraud = int(((logo == 1) & (fraud == 1)).sum())
    with_logo_non = int(((logo == 1) & (fraud == 0)).sum())
    no_logo_fraud = int(((logo == 0) & (fraud == 1)).sum())
    no_logo_non = int(((logo == 0) & (fraud == 0)).sum())

    section5 = {
        "labels": ["有公司Logo", "無公司Logo"],
        "prodA": [with_logo_fraud, no_logo_fraud],
        "prodB": [with_logo_non, no_logo_non],
    }

    # 7) Section6：堆疊圖 - 以國家(top 6) 為 labels，堆疊三個特徵筆數
    # 轉成 ISO3 讓前端 GeoJSON 能對上
    df_country = df.copy()
    df_country["iso3"] = df_country["country"].apply(_safe_iso2_to_iso3)
    df_country = df_country.dropna(subset=["iso3"])
    top_iso3 = df_country["iso3"].value_counts().head(6).index.tolist()

    def _count_feature(feature_col: str) -> List[int]:
        out = []
        series = (
            pd.to_numeric(df_country[feature_col], errors="coerce")
            .fillna(0)
            .astype(int)
        )
        for code in top_iso3:
            out.append(int(((df_country["iso3"] == code) & (series == 1)).sum()))
        return out

    section6 = {
        "labels": top_iso3,
        "external": _count_feature("telecommuting"),
        "internal": _count_feature("has_company_logo"),
        "other": _count_feature("has_questions"),
    }

    # 8) Section7：散點圖 - 每種 employment_type 一個點 (x=有Logo%, y=有問題%)
    scatter_points: List[Dict[str, float]] = []
    for emp, g in df.groupby(df["employment_type"].fillna("Unknown").astype(str)):
        if len(scatter_points) >= 25:
            break
        x = float(
            pd.to_numeric(g["has_company_logo"], errors="coerce").fillna(0).mean() * 100
        )
        y = float(
            pd.to_numeric(g["has_questions"], errors="coerce").fillna(0).mean() * 100
        )
        scatter_points.append({"x": round(x, 2), "y": round(y, 2)})

    # 9) Map：iso3 -> count
    map_counts = df_country["iso3"].value_counts().head(12)
    map_data = {k: int(v) for k, v in map_counts.items()}
    map_names = {k: _country_name_en(k) for k in map_data.keys()}

    # 10) Tables：維持前端固定 header 的格式(三欄)
    # table1：用 top6 國家筆數當作「月份/銷售額/成長率」占位
    months = ["一月", "二月", "三月", "四月", "五月", "六月"]
    vals = map_counts.head(6).values.astype(int).tolist()
    while len(vals) < 6:
        vals.append(0)

    growth = []
    prev = None
    for v in vals[:6]:
        if prev in (None, 0):
            growth.append("+")
        else:
            growth.append(f"{round((v - prev) / prev * 100, 1)}%")
        prev = v

    table1 = [[m, str(v), g] for m, v, g in zip(months, vals[:6], growth)]

    # table2：top6 title (fraudulent) 當作「產品/銷量/評分」占位
    top_titles_6 = top_titles.head(6)
    table2 = []
    for title, cnt in top_titles_6.items():
        score = (
            5.0
            if cnt == 0
            else round(min(5.0, 3.5 + (cnt / max(1, top_titles_6.max())) * 1.5), 1)
        )
        table2.append(
            [title[:22] + ("…" if len(title) > 22 else ""), str(int(cnt)), str(score)]
        )

    payload = {
        "ranking": {"labels": ranking_labels, "values": ranking_values},
        "charts": {
            "section1": section1,
            "section2": section2,
            "section3": section3,
            "section4": section4,
            "section5": section5,
            "section6": section6,
            "section7": scatter_points,
        },
        "map": map_data,
        "map_names": map_names,
        "tables": {"table1": table1, "table2": table2},
    }

    return jsonify(payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)

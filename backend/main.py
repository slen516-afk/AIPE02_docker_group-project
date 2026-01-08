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

    # 1) Ranking：詐騙 (fraudulent=1) 前 5 名 title
    fraud_flag = pd.to_numeric(df["fraudulent"], errors="coerce").fillna(0).astype(int)
    fraud_df = df[fraud_flag == 1]
    top_titles = fraud_df["title"].fillna("Unknown").astype(str).value_counts().head(5)
    ranking_labels = [
        str(x) if pd.notna(x) else "Unknown" for x in top_titles.index.tolist()
    ]
    ranking_values = top_titles.values.astype(int).tolist()

    # 2) Section1：圓餅圖 - 詐騙 vs 非詐騙
    fraud_counts = fraud_flag.value_counts().reindex([0, 1], fill_value=0)
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
    tmp4 = df.copy()
    tmp4["employment_type"] = tmp4["employment_type"].fillna("Unknown").astype(str)
    tmp4["industry_group"] = tmp4["industry_group"].fillna("Unknown").astype(str)

    fraud_only = tmp4[
        pd.to_numeric(tmp4["fraudulent"], errors="coerce").fillna(0).astype(int) == 1
    ]

    def _pct(mask) -> float:
        if len(fraud_only) == 0:
            return 0.0
        return float(mask.mean() * 100)

    logo = (
        pd.to_numeric(fraud_only["has_company_logo"], errors="coerce")
        .fillna(0)
        .astype(int)
    )
    ques = (
        pd.to_numeric(fraud_only["has_questions"], errors="coerce")
        .fillna(0)
        .astype(int)
    )
    tele = (
        pd.to_numeric(fraud_only["telecommuting"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    section4 = {
        "labels": ["遠端", "無公司Logo", "無面試題目", "聘僱型態未知", "產業未知"],
        "values": [
            round(_pct(tele == 1), 2),
            round(_pct(logo == 0), 2),
            round(_pct(ques == 0), 2),
            round(_pct(fraud_only["employment_type"] == "Unknown"), 2),
            round(_pct(fraud_only["industry_group"] == "Unknown"), 2),
        ],
    }

    # 6) Section5：分組直條圖 - 有Logo/無Logo 的 詐騙 vs 非詐騙
    logo = pd.to_numeric(df["has_company_logo"], errors="coerce").fillna(0).astype(int)
    fraud = fraud_flag
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

    def _count_feature(feature_col: str, target: int = 1) -> List[int]:
        out = []
        series = (
            pd.to_numeric(df_country[feature_col], errors="coerce")
            .fillna(0)
            .astype(int)
        )
        for code in top_iso3:
            out.append(int(((df_country["iso3"] == code) & (series == target)).sum()))
        return out

    section6 = {
        "labels": top_iso3,
        # 以「紅旗」定義：遠端(=1)、無Logo(=0)、無Questions(=0)
        "external": _count_feature("telecommuting", 1),
        "internal": _count_feature("has_company_logo", 0),
        "other": _count_feature("has_questions", 0),
    }

    # 8) Section7：散點圖 - 每種 employment_type 一個點 (x=有Logo%, y=有問題%)
    scatter_points: List[Dict[str, float]] = []

    tmp = df.copy()
    tmp["employment_type"] = tmp["employment_type"].fillna("Unknown").astype(str)

    # 先算每個 employment_type 的統計，並用筆數排序
    stats = (
        tmp.groupby("employment_type", dropna=False)
        .agg(
            count=("employment_type", "size"),
            logo_rate=(
                "has_company_logo",
                lambda s: pd.to_numeric(s, errors="coerce").fillna(0).mean() * 100,
            ),
            question_rate=(
                "has_questions",
                lambda s: pd.to_numeric(s, errors="coerce").fillna(0).mean() * 100,
            ),
            fraud_rate=(
                "fraudulent",
                lambda s: pd.to_numeric(s, errors="coerce").fillna(0).mean() * 100,
            ),
        )
        .reset_index()
        .sort_values("count", ascending=False)
    )

    for _, r in stats.iterrows():
        scatter_points.append(
            {
                "x": round(float(r["logo_rate"]), 2),
                "y": round(float(r["question_rate"]), 2),
                "label": str(r["employment_type"]),  # 這個點是誰
                "count": int(r["count"]),  # 樣本數
                "fraud_rate": round(float(r["fraud_rate"]), 2),  # 詐騙率
            }
        )

    # 9) Map：iso3 -> count
    map_counts = df_country["iso3"].value_counts().head(12)
    map_data = {k: int(v) for k, v in map_counts.items()}
    map_names = {k: _country_name_en(k) for k in map_data.keys()}

    # 10) Tables：維持前端固定三欄格式(三欄)

    tmp = df.copy()
    tmp["employment_type"] = tmp["employment_type"].fillna("Unknown").astype(str)

    tmp = tmp[fraud_flag == 1]

    etype_counts = tmp["employment_type"].value_counts().head(6)
    labels = etype_counts.index.tolist()
    vals = etype_counts.values.astype(int).tolist()

    total = sum(vals) if sum(vals) > 0 else 1
    shares = [round(v / total * 100, 1) for v in vals]

    # table1 三欄：聘僱型態 / 可疑職缺數 / 占比(%)
    table1 = [[lab, str(v), f"{s}%"] for lab, v, s in zip(labels, vals, shares)]

    # table2：紅旗特徵 Top 6（特徵 / 命中次數 / 可疑度）
    base = df.copy()
    base["employment_type"] = base["employment_type"].fillna("Unknown").astype(str)
    base["industry_group"] = base["industry_group"].fillna("Unknown").astype(str)
    base["edu_level"] = base["edu_level"].fillna("Unknown").astype(str)

    fraud_flag = (
        pd.to_numeric(base["fraudulent"], errors="coerce").fillna(0).astype(int)
    )
    fraud_df2 = base[fraud_flag == 1]
    non_df2 = base[fraud_flag == 0]

    def _i01(s):
        return pd.to_numeric(s, errors="coerce").fillna(0).astype(int)

    # 候選紅旗（都能從 cleaned_data_revise_2.csv 取到）
    candidates = [
        ("無公司Logo", lambda d: _i01(d["has_company_logo"]) == 0),
        ("無面試題目(Questions)", lambda d: _i01(d["has_questions"]) == 0),
        ("遠端(telecommuting)", lambda d: _i01(d["telecommuting"]) == 1),
        ("聘僱型態未知", lambda d: d["employment_type"] == "Unknown"),
        ("產業未知", lambda d: d["industry_group"] == "Unknown"),
        ("學歷未知", lambda d: d["edu_level"] == "Unknown"),
    ]

    stats2 = []
    for name, fn in candidates:
        mf = fn(fraud_df2) if len(fraud_df2) else pd.Series([], dtype=bool)
        mn = fn(non_df2) if len(non_df2) else pd.Series([], dtype=bool)

        hit = int(mf.sum()) if len(fraud_df2) else 0
        fr = float(mf.mean()) if len(fraud_df2) else 0.0
        nr = float(mn.mean()) if len(non_df2) else 0.0
        lift = fr / (nr + 1e-9) if nr > 0 else (fr / 1e-9 if fr > 0 else 1.0)

        stats2.append({"name": name, "hit": hit, "lift": lift})

    # lift -> 1~5 分（越高越可疑）
    max_lift = max([x["lift"] for x in stats2], default=1.0)
    for x in stats2:
        if max_lift <= 1.0:
            score = 1.0
        else:
            score = 1.0 + (x["lift"] - 1.0) / (max_lift - 1.0) * 4.0
        x["score"] = round(min(5.0, max(1.0, score)), 1)

    top6 = sorted(stats2, key=lambda x: x["lift"], reverse=True)[:6]
    table2 = [[x["name"], str(x["hit"]), str(x["score"])] for x in top6]

    # 11) 組合回傳（前端固定使用 allData.ranking / allData.charts / allData.tables / allData.map）
    return jsonify(
        {
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
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)

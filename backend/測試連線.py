import pymysql  # 1. 務必加上這行

connection = pymysql.connect(
    host="db",  # Docker 內部連線用服務名稱
    port=3306,  # 容器內部的 Port
    user="admin",  # 你設定的非 root 帳號
    password="password",  # 你設定的密碼
    database="project_db",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)

# 測試是否連線成功
print("連線成功！")
connection.close()

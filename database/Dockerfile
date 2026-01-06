FROM mysql:8.0

# 資料庫第一次初始化時自動執行（/var/lib/mysql 為空時）
COPY init.sql /docker-entrypoint-initdb.d/init.sql

# CSV 放在 mysql 容器預設可用的匯入目錄
COPY import/cleaned_data_revise_2.csv /var/lib/mysql-files/cleaned_data_revise_2.csv

# 移除 Windows 換行符號
RUN sed -i 's/\r$//' /docker-entrypoint-initdb.d/init.sql \
    && sed -i 's/\r$//' /var/lib/mysql-files/cleaned_data_revise_2.csv

-- 1. 加入這行：暫時關閉嚴格模式，容許資料缺漏
SET SESSION sql_mode = '';

CREATE DATABASE IF NOT EXISTS project_db;
USE project_db;

DROP TABLE IF EXISTS temp_raw_data;

CREATE TABLE temp_raw_data (
    title VARCHAR(255),
    telecommuting TINYINT,
    has_company_logo TINYINT,
    has_questions TINYINT,
    employment_type VARCHAR(100),
    fraudulent TINYINT,
    in_balanced_dataset TINYINT,
    country VARCHAR(100),
    industry_group VARCHAR(255),
    edu_level VARCHAR(100)
);

LOAD DATA INFILE '/var/lib/mysql-files/cleaned_data_revise_2.csv'
INTO TABLE temp_raw_data
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
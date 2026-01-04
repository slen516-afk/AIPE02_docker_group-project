CREATE DATABASE IF NOT EXISTS project_db;
USE project_db;

CREATE TABLE IF NOT EXISTS temp_raw_data (
    title VARCHAR(255),
    telecommuting TINYINT,
    has_company_logo TINYINT,
    has_questions TINYINT,
    employment_type VARCHAR(100),
    fraudulent TINYINT,
    in_balanced_dataset TINYINT,
    country VARCHAR(100),
    industry_group VARCHAR(100),
    edu_level VARCHAR(100)
);
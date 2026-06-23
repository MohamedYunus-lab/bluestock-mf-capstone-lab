CREATE TABLE fund_master (
    scheme_code TEXT PRIMARY KEY,
    scheme_name TEXT,
    category TEXT,
    fund_house TEXT
);

CREATE TABLE nav_history (
    scheme_code TEXT,
    date DATE,
    nav REAL
);

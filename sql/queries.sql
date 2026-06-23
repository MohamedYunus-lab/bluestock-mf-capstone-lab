-- Count funds by category
SELECT category, COUNT(*) 
FROM fund_master 
GROUP BY category;

-- Average NAV per scheme
SELECT scheme_code, AVG(nav) 
FROM nav_history 
GROUP BY scheme_code;

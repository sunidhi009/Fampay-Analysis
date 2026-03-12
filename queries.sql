-- 1. ONBOARDING FUNNEL: How many users complete each stage?
SELECT
    stage,
    COUNT(DISTINCT user_id) AS users_reached,
    ROUND(COUNT(DISTINCT user_id) * 100.0 /
        (SELECT COUNT(DISTINCT user_id) FROM funnel_events
         WHERE stage = 'app_downloaded'), 1) AS pct_of_top
FROM funnel_events
GROUP BY stage
ORDER BY
    CASE stage
        WHEN 'app_downloaded' THEN 1
        WHEN 'registered' THEN 2
        WHEN 'kyc_completed' THEN 3
        WHEN 'card_activated' THEN 4
        WHEN 'first_transaction' THEN 5
    END;

-- 2. CHURN RATE BY CITY TIER
SELECT
    city_tier,
    COUNT(DISTINCT u.user_id) AS total_users,
    SUM(card_activated) AS activated_users,
    ROUND(SUM(card_activated) * 100.0 / COUNT(*), 1) AS activation_rate
FROM users u
GROUP BY city_tier;

-- 3. COHORT RETENTION: D1, D7, D30
SELECT
    strftime('%Y-%m', signup_date) AS signup_cohort,
    COUNT(DISTINCT u.user_id) AS cohort_size,
    COUNT(DISTINCT CASE
        WHEN julianday(t.txn_date) - julianday(u.signup_date) <= 1
        THEN u.user_id END) AS day1_retained,
    COUNT(DISTINCT CASE
        WHEN julianday(t.txn_date) - julianday(u.signup_date) <= 7
        THEN u.user_id END) AS day7_retained,
    COUNT(DISTINCT CASE
        WHEN julianday(t.txn_date) - julianday(u.signup_date) <= 30
        THEN u.user_id END) AS day30_retained
FROM users u
LEFT JOIN transactions t ON u.user_id = t.user_id AND t.status = 'success'
GROUP BY signup_cohort
ORDER BY signup_cohort;

-- 4. PAYMENT METHOD BREAKDOWN
SELECT
    txn_type,
    COUNT(*) AS total_txns,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct_share,
    ROUND(AVG(amount), 2) AS avg_amount,
    SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) AS failed_txns,
    ROUND(SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) * 100.0
        / COUNT(*), 1) AS failure_rate
FROM transactions
GROUP BY txn_type;

-- 5. TOP SPENDING CATEGORIES BY AGE GROUP
SELECT
    CASE
        WHEN u.age BETWEEN 13 AND 15 THEN '13-15'
        WHEN u.age BETWEEN 16 AND 18 THEN '16-18'
        WHEN u.age BETWEEN 19 AND 21 THEN '19-21'
        ELSE '22-25'
    END AS age_group,
    t.category,
    COUNT(*) AS txn_count,
    ROUND(AVG(t.amount), 2) AS avg_spend
FROM transactions t
JOIN users u ON t.user_id = u.user_id
WHERE t.status = 'success'
GROUP BY age_group, category
ORDER BY age_group, txn_count DESC;

-- 6. HIGH VALUE USER SEGMENTS
SELECT
    u.user_id,
    u.age,
    u.city_tier,
    COUNT(t.txn_id) AS total_txns,
    ROUND(SUM(t.amount), 2) AS total_spend,
    ROUND(AVG(t.amount), 2) AS avg_txn
FROM users u
JOIN transactions t ON u.user_id = t.user_id
WHERE t.status = 'success'
GROUP BY u.user_id
HAVING total_txns >= 10
ORDER BY total_spend DESC
LIMIT 20;
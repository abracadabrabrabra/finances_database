CREATE VIEW user_financial_summary AS
SELECT
    u.id,
    u.email,
    u.full_name,
    COUNT(DISTINCT a.id) as total_accounts,
    COUNT(t.id) as total_transactions,
    SUM(CASE WHEN t.type = 'income' THEN t.amount ELSE 0 END) as total_income,
    SUM(CASE WHEN t.type = 'expense' THEN t.amount ELSE 0 END) as total_expense,
    SUM(CASE WHEN t.type = 'income' THEN t.amount ELSE -t.amount END) as net_savings
FROM users u
    LEFT JOIN accounts a ON a.user_id = u.id
    LEFT JOIN transactions t ON t.account_id = a.id
GROUP BY u.id, u.email, u.full_name;


CREATE VIEW goal_progress AS
SELECT
    g.name as goal_name,
    u.email,
    a.name as account_name,
    g.target_amount,
    COALESCE(SUM(t.amount), 0) as saved_amount,
    ROUND(COALESCE(SUM(t.amount), 0) / g.target_amount * 100, 2) as progress_percent,
    g.deadline,
        CASE
        WHEN CURRENT_DATE > g.deadline AND COALESCE(SUM(t.amount), 0) < g.target_amount THEN 'overdue'
        WHEN COALESCE(SUM(t.amount), 0) >= g.target_amount THEN 'achieved'
        ELSE 'in_progress'
        END as status
FROM goals g
    JOIN accounts a ON a.id = g.account_id
    JOIN users u ON u.id = a.user_id
    LEFT JOIN transactions t ON t.goal_id = g.id AND t.type = 'income'
WHERE g.status = 'active'
GROUP BY g.id, g.name, u.email, a.name, g.target_amount, g.deadline;
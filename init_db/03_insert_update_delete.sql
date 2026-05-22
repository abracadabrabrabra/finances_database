INSERT INTO transactions (account_id, category_id, goal_id, amount, type, description, transaction_date)
VALUES (
           (SELECT id FROM accounts WHERE name = 'VTB card' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
           (SELECT id FROM categories WHERE name = 'Salary' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
           (SELECT id FROM goals WHERE name = 'Save up for car' AND account_id = (SELECT id FROM accounts WHERE name = 'VTB card' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com'))),
           75000.00, 'income', 'April salary on second job', '2026-04-02');


INSERT INTO transactions (account_id, category_id, goal_id, amount, type, description, transaction_date)
VALUES (
           (SELECT id FROM accounts WHERE name = 'Cash' AND user_id = (SELECT id FROM users WHERE email = 'maria@example.com')),
           (SELECT id FROM categories WHERE name = 'Salary' AND user_id = (SELECT id FROM users WHERE email = 'maria@example.com')),
           (SELECT id FROM goals WHERE name = 'Plastic surgery' AND account_id = (SELECT id FROM accounts WHERE name = 'Cash' AND user_id = (SELECT id FROM users WHERE email = 'maria@example.com'))),
           50000.00, 'income', 'March salary on second job', '2026-03-31');


INSERT INTO transactions (account_id, category_id, import_log_id, amount, type, description, transaction_date)
VALUES
    (
        (SELECT id FROM accounts WHERE name = 'VTB card' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
        (SELECT id FROM categories WHERE name = 'Freelance' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
        (SELECT id FROM import_logs WHERE user_id = (SELECT id FROM users WHERE email = 'alex@example.com') AND file_name = 'import_alex_2026_03_22.csv'),
        5000.00, 'income', 'Bet paid off', '2026-03-15');

INSERT INTO transactions (account_id, category_id, import_log_id, amount, type, description, transaction_date)
VALUES
    (
        (SELECT id FROM accounts WHERE name = 'VTB card' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
        (SELECT id FROM categories WHERE name = 'Freelance' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
        (SELECT id FROM import_logs WHERE user_id = (SELECT id FROM users WHERE email = 'alex@example.com') AND file_name = 'import_alex_2026_03_22.csv'),
        50000.00, 'expense', 'Lost money in online casino', '2026-03-17');

INSERT INTO transactions (account_id, category_id, import_log_id, amount, type, description, transaction_date)
VALUES
    (
        (SELECT id FROM accounts WHERE name = 'Sberbank card' AND user_id = (SELECT id FROM users WHERE email = 'maria@example.com')),
        (SELECT id FROM categories WHERE name = 'Clothes' AND user_id = (SELECT id FROM users WHERE email = 'maria@example.com')),
        (SELECT id FROM import_logs WHERE user_id = (SELECT id FROM users WHERE email = 'maria@example.com') AND file_name = 'import_maria_2026_04_01.csv'),
        5000.00, 'expense', 'New dress', '2026-04-01' );



-------


UPDATE users
SET full_name = 'Pushkin Alexey Ivanovich', updated_at = CURRENT_TIMESTAMP
WHERE email = 'alex@example.com';

UPDATE goals
SET target_amount = 4000000.00, updated_at = CURRENT_TIMESTAMP
WHERE name = 'Save up for car';

UPDATE users
SET password_hash = 'hash_789', updated_at = CURRENT_TIMESTAMP
WHERE email = 'maria@example.com';

INSERT INTO categories (user_id, name, description)
VALUES ((SELECT id FROM users WHERE email = 'alex@example.com'), 'Entertainment', 'Casino games');

UPDATE transactions
SET category_id = (
    SELECT id FROM categories
    WHERE name = 'Entertainment' AND user_id = (
        SELECT user_id FROM accounts WHERE id = transactions.account_id
    )
),
    description = 'Online casino loss',
    updated_at = CURRENT_TIMESTAMP
WHERE description = 'Lost money in online casino';

UPDATE transactions
SET amount = 2500, description = 'CORRECTED: ' || description
WHERE id = (SELECT id from transactions WHERE description = 'Bet paid off');


-------

DELETE FROM import_logs WHERE rows_succeeded = 0;

DELETE FROM accounts
WHERE id NOT IN (SELECT DISTINCT account_id FROM transactions)
  AND created_at > '2025-01-16';

DELETE FROM import_logs
WHERE created_at < CURRENT_DATE - INTERVAL '1 year';



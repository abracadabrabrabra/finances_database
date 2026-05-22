INSERT INTO users (email, password_hash, full_name, created_at) VALUES
    ('alex@example.com', 'hash_123', 'Ivanov Alexey Petrovich', '2025-01-01'),
    ('maria@example.com', 'hash_456', 'Petrova Maria Sergeevna', '2025-01-01');

INSERT INTO categories (user_id, name, description) VALUES 
    ((SELECT id FROM users WHERE email = 'alex@example.com'), 'Products', 'Buying food'),
    ((SELECT id FROM users WHERE email = 'alex@example.com'), 'Transport', 'Taxi, metro, fuel'),
    ((SELECT id FROM users WHERE email = 'alex@example.com'), 'Cafe', 'Cafe & restaurants'),
    ((SELECT id FROM users WHERE email = 'alex@example.com'), 'Salary', 'Income from working'),
    ((SELECT id FROM users WHERE email = 'alex@example.com'), 'Freelance', 'Additional income');

INSERT INTO categories (user_id, name, description) VALUES 
    ((SELECT id FROM users WHERE email = 'maria@example.com'), 'Products', 'Buying food'),
    ((SELECT id FROM users WHERE email = 'maria@example.com'), 'Clothes', 'Buying clothes'),
    ((SELECT id FROM users WHERE email = 'maria@example.com'), 'Entertainment', 'Cinema, theatre'),
    ((SELECT id FROM users WHERE email = 'maria@example.com'), 'Salary', 'Income from working');

INSERT INTO accounts (user_id, name, currency, initial_balance, type, created_at) VALUES
    ((SELECT id FROM users WHERE email = 'alex@example.com'), 'VTB card', 'RUB', 200000.00, 'credit_card', '2025-02-14'),
    ((SELECT id FROM users WHERE email = 'alex@example.com'), 'Bank of America card', 'USD', 0.00, 'credit_card', '2025-01-18'),
    ((SELECT id FROM users WHERE email = 'alex@example.com'), 'Cash', 'RUB', 15000.00, 'cash', '2025-06-25'),

    ((SELECT id FROM users WHERE email = 'maria@example.com'), 'Cash', 'RUB', 75000.00, 'cash', '2025-06-25'),
    ((SELECT id FROM users WHERE email = 'maria@example.com'), 'Sberbank card', 'RUB', 10000.00, 'credit_card', '2025-01-16');


INSERT INTO goals (account_id, name, target_amount, deadline, status) VALUES 
	((SELECT id FROM accounts WHERE name = 'VTB card' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
    	'Save up for car',
        3500000.00,
        '2026-12-31',
        'active'
    ),
    ((SELECT id FROM accounts WHERE name = 'Bank of America card' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
        'Safety cushion',
        300000.00,
        '2026-06-30',
        'active'
    ),
    ((SELECT id FROM accounts WHERE name = 'Cash' AND user_id = (SELECT id FROM users WHERE email = 'maria@example.com')),
        'Plastic surgery',
        2000000.00,
        '2026-08-15',
        'active'
    );

INSERT INTO exchange_rates_usd (target_currency, rate, date)
SELECT 
    currency,
    round((random() * 30 + 70)::numeric, 4),
    CURRENT_DATE - (generate_series * interval '1 day')
FROM 
    generate_series(0, 89) AS generate_series,
    (VALUES ('RUB'), ('EUR'), ('GBP'), ('CNY')) AS currencies(currency);

INSERT INTO import_logs (user_id, file_name, rows_processed, rows_succeeded, error_message) VALUES 
    ((SELECT id FROM users WHERE email = 'alex@example.com'),
        'import_alex_2026_03_22.csv',
        2,
        2,
        NULL
    ),
    ((SELECT id FROM users WHERE email = 'alex@example.com'),
        'import_alex_2026_04_01.csv',
        200,
        0,
        'ERROR: invalid data format'
    ),
    ((SELECT id FROM users WHERE email = 'maria@example.com'),
        'import_maria_2026_04_01.csv',
        1,
        1,
        NULL
    );


INSERT INTO transactions (account_id, category_id, amount, type, description, transaction_date)
VALUES 
    (
        (SELECT id FROM accounts WHERE name = 'VTB card' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
        (SELECT id FROM categories WHERE name = 'Products' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
        3450.50, 'expense', '5ka', '2026-04-03'
    ),
    (
        (SELECT id FROM accounts WHERE name = 'VTB card' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
        (SELECT id FROM categories WHERE name = 'Transport' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
        500.00, 'expense', 'yandex taxi', '2026-04-02'
    ),
    (
        (SELECT id FROM accounts WHERE name = 'Cash' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
        (SELECT id FROM categories WHERE name = 'Cafe' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
        1250.00, 'expense', 'Cofee house', '2026-04-02'
    );

INSERT INTO transactions (account_id, category_id, amount, type, description, transaction_date)
VALUES 
    (
        (SELECT id FROM accounts WHERE name = 'VTB card' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
        (SELECT id FROM categories WHERE name = 'Salary' AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com')),
        150000.00, 'income', 'March salary', '2026-03-31'
    );

INSERT INTO transactions (account_id, category_id, amount, type, description, transaction_date)
VALUES (
    (SELECT id FROM accounts WHERE name = 'Cash' AND user_id = (SELECT id FROM users WHERE email = 'maria@example.com')),
    (SELECT id FROM categories WHERE name = 'Salary' AND user_id = (SELECT id FROM users WHERE email = 'maria@example.com')),
    120000.00, 'income', 'April salary', '2026-04-02'
);
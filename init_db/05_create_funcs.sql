CREATE OR REPLACE FUNCTION get_account_balance(p_account_id UUID)
RETURNS TABLE(balance_calc DECIMAL, currency VARCHAR, last_transaction_date DATE) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(a.initial_balance + SUM(
            CASE
                WHEN t.type = 'income' THEN t.amount
                WHEN t.type = 'expense' THEN -t.amount
                WHEN t.type = 'transfer' AND t.account_id = p_account_id THEN -t.amount
                ELSE 0
            END
        ), a.initial_balance) AS balance_calc,
        a.currency,
        MAX(t.transaction_date) AS last_transaction_date
    FROM accounts a
    LEFT JOIN transactions t ON t.account_id = a.id
    WHERE a.id = p_account_id
    GROUP BY a.id, a.initial_balance, a.currency;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account with ID % not found', p_account_id;
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION check_transfer_eligibility(
    p_from_account_id UUID,
    p_to_account_id UUID,
    p_amount DECIMAL,
    OUT is_possible BOOLEAN,
    OUT fee DECIMAL,
    OUT message TEXT
) AS $$
DECLARE
    v_from_balance DECIMAL;
    v_from_currency VARCHAR(3);
    v_to_currency VARCHAR(3);
BEGIN
    IF p_amount <= 0 THEN
        is_possible := FALSE;
        fee := 0;
        message := 'Amount must be positive';
        RETURN;
    END IF;

    BEGIN
        SELECT balance_calc, currency INTO v_from_balance, v_from_currency
        FROM get_account_balance(p_from_account_id);

        SELECT currency INTO v_to_currency
        FROM accounts WHERE id = p_to_account_id;

        EXCEPTION
            WHEN OTHERS THEN
                is_possible := FALSE;
                fee := 0;
                message := 'Error accessing account data: ' || SQLERRM;
                RETURN;
    END;

    IF p_from_account_id = p_to_account_id THEN
        is_possible := FALSE;
        fee := 0;
        message := 'Error: similar accounts';
        RETURN;
    END IF;

    IF v_from_currency != v_to_currency THEN
        is_possible := FALSE;
        fee := 0;
        message := format('Currency conversion not supported. From: %s, To: %s',
            v_from_currency, v_to_currency);
        RETURN;
    END IF;

    IF p_amount > v_from_balance THEN
        is_possible := FALSE;
        fee := 0;
        message := format('Not enough money. Available: %s %s',
            round(v_from_balance, 2), v_from_currency);
        RETURN;
    END IF;

    fee := 0;
    is_possible := TRUE;
    message := 'OK';

    EXCEPTION
        WHEN OTHERS THEN
            is_possible := FALSE;
            fee := 0;
            message := 'System error: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE transfer_money(
    p_from_account_id UUID,
    p_to_account_id UUID,
    p_amount DECIMAL,
    p_description TEXT DEFAULT 'Money transfer'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_is_possible BOOLEAN;
    v_fee DECIMAL;
    v_message TEXT;
    v_category_id UUID;
    v_commission_category_id UUID;
BEGIN
    SELECT * INTO v_is_possible, v_fee, v_message
    FROM check_transfer_eligibility(p_from_account_id, p_to_account_id, p_amount);

    IF NOT v_is_possible THEN
        RAISE EXCEPTION 'Error checking: %', v_message;
    END IF;

    BEGIN
        SELECT id INTO v_category_id FROM categories
        WHERE name = 'Transfer' AND user_id = (SELECT user_id FROM accounts WHERE id = p_from_account_id);

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Category "Transfer" not found for this user';
        END IF;

        SELECT id INTO v_commission_category_id FROM categories
        WHERE name = 'Commission' AND user_id = (SELECT user_id FROM accounts WHERE id = p_from_account_id);

        INSERT INTO transactions (
            account_id, category_id, amount, type, description, transaction_date
        ) VALUES (
             p_from_account_id,
             v_category_id,
             p_amount + v_fee,
             'expense',
             p_description || ' (outgoing)',
             CURRENT_DATE
         );

        INSERT INTO transactions (
            account_id, category_id, amount, type, description, transaction_date
        ) VALUES (
             p_to_account_id,
             v_category_id,
             p_amount,
             'income',
             p_description || ' (incoming)',
             CURRENT_DATE
         );

        IF v_fee > 0 AND v_commission_category_id IS NOT NULL THEN
            INSERT INTO transactions (
                account_id, category_id, amount, type, description, transaction_date
            ) VALUES (
                p_from_account_id,
                v_commission_category_id,
                v_fee,
                'expense',
                'Transfer commission',
                CURRENT_DATE
            );
        ELSIF v_fee > 0 THEN
            RAISE NOTICE 'Commission category not found, but fee % was not charged (no commission in same currency)', v_fee;
        END IF;

        RAISE NOTICE 'Transfer was successful. Amount: %, Commission: %', p_amount, v_fee;

        EXCEPTION
                WHEN unique_violation THEN
                    RAISE NOTICE 'Unique violation error: %', SQLERRM;
                    RAISE EXCEPTION 'Transaction conflict: duplicate entry detected';
                WHEN foreign_key_violation THEN
                    RAISE NOTICE 'Foreign key violation: %', SQLERRM;
                    RAISE EXCEPTION 'Referenced account or category does not exist';
                WHEN check_violation THEN
                    RAISE NOTICE 'Check constraint violation: %', SQLERRM;
                    RAISE EXCEPTION 'Data validation failed (e.g., amount must be positive)';
                WHEN not_null_violation THEN
                    RAISE NOTICE 'Not null violation: %', SQLERRM;
                    RAISE EXCEPTION 'Required field is missing';
                WHEN OTHERS THEN
                    RAISE NOTICE 'Unexpected error: %', SQLERRM;
                    RAISE;
    END;
END;
$$;


INSERT INTO categories (user_id, name, description) VALUES
    ((SELECT id FROM users WHERE email = 'alex@example.com'),
    'Transfer',
    'Money transfers between accounts'),
    ((SELECT id FROM users WHERE email = 'alex@example.com'),
    'Commission',
    'Bank fees and currency conversion fees');

INSERT INTO categories (user_id, name, description) VALUES
    ((SELECT id FROM users WHERE email = 'maria@example.com'),
    'Transfer',
    'Money transfers between accounts'),
    ((SELECT id FROM users WHERE email = 'maria@example.com'),
    'Commission',
    'Bank fees and currency conversion fees');


SELECT id FROM accounts
WHERE name = 'VTB card'
  AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com');

SELECT id FROM accounts
WHERE name = 'Cash'
  AND user_id = (SELECT id FROM users WHERE email = 'alex@example.com');
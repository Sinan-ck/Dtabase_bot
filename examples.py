"""Few-shot examples: each one is a question plus the correct MySQL query."""

DISCOUNTED = "t.price * t.stock_quantity * (1 - COALESCE(d.pct_discount, 0) / 100)"

EXAMPLES = [
    {
        "question": "Which brand has the highest total inventory value?",
        "sql": """SELECT brand, SUM(price * stock_quantity) AS inventory_value
FROM t_shirts
GROUP BY brand
ORDER BY inventory_value DESC
LIMIT 1;""",
    },
    {
        "question": "What is the average price of t-shirts?",
        "sql": "SELECT AVG(price) FROM t_shirts;",
    },
    {
        "question": "Which brand has the highest total stock quantity?",
        "sql": """SELECT brand, SUM(stock_quantity) AS total_stock
FROM t_shirts
GROUP BY brand
ORDER BY total_stock DESC
LIMIT 1;""",
    },
    {
        "question": "Find the top 3 most expensive t-shirts.",
        "sql": """SELECT t_shirt_id, brand, price
FROM t_shirts
ORDER BY price DESC
LIMIT 3;""",
    },
    {
        "question": "Find all products whose stock quantity is greater than the average stock quantity.",
        "sql": """SELECT *
FROM t_shirts
WHERE stock_quantity > (SELECT AVG(stock_quantity) FROM t_shirts);""",
    },
    {
        "question": "For each brand, calculate total stock quantity and average price.",
        "sql": """SELECT brand, SUM(stock_quantity) AS total_stock, AVG(price) AS average_price
FROM t_shirts
GROUP BY brand;""",
    },
    {
        "question": "What is the total inventory value after applying discounts?",
        "sql": f"""SELECT SUM({DISCOUNTED}) AS total_inventory_value
FROM t_shirts t
LEFT JOIN discounts d ON t.t_shirt_id = d.t_shirt_id;""",
    },
    {
        "question": "Rank all brands by their total inventory value after applying discounts from highest to lowest.",
        "sql": f"""SELECT t.brand, SUM({DISCOUNTED}) AS inventory_value
FROM t_shirts t
LEFT JOIN discounts d ON t.t_shirt_id = d.t_shirt_id
GROUP BY t.brand
ORDER BY inventory_value DESC;""",
    },
    {
        "question": "For each brand, calculate the total amount saved through discounts.",
        "sql": """SELECT t.brand,
       SUM(t.price * t.stock_quantity * COALESCE(d.pct_discount, 0) / 100) AS total_savings
FROM t_shirts t
LEFT JOIN discounts d ON t.t_shirt_id = d.t_shirt_id
GROUP BY t.brand
ORDER BY total_savings DESC;""",
    },
    {
        "question": "Find the t-shirt with the highest discounted price.",
        "sql": """SELECT t.t_shirt_id, t.brand, t.price, d.pct_discount,
       t.price * (1 - COALESCE(d.pct_discount, 0) / 100) AS discounted_price
FROM t_shirts t
LEFT JOIN discounts d ON t.t_shirt_id = d.t_shirt_id
ORDER BY discounted_price DESC
LIMIT 1;""",
    },
    {
        "question": "Find brands whose average price is higher than the overall average price.",
        "sql": """SELECT brand, AVG(price) AS average_price
FROM t_shirts
GROUP BY brand
HAVING AVG(price) > (SELECT AVG(price) FROM t_shirts);""",
    },
    {
        "question": "Find the second most expensive t-shirt after applying the discount.",
        "sql": """SELECT t.t_shirt_id, t.brand, t.price, d.pct_discount,
       t.price * (1 - COALESCE(d.pct_discount, 0) / 100) AS discounted_price
FROM t_shirts t
LEFT JOIN discounts d ON t.t_shirt_id = d.t_shirt_id
ORDER BY discounted_price DESC
LIMIT 1 OFFSET 1;""",
    },
    {
        "question": "For each brand, calculate total inventory value before and after discount.",
        "sql": f"""SELECT t.brand,
       SUM(t.price * t.stock_quantity) AS value_before_discount,
       SUM({DISCOUNTED}) AS value_after_discount
FROM t_shirts t
LEFT JOIN discounts d ON t.t_shirt_id = d.t_shirt_id
GROUP BY t.brand;""",
    },
    {
        "question": "Find the brand with the second highest total inventory value after discounts.",
        "sql": f"""SELECT t.brand, SUM({DISCOUNTED}) AS inventory_value
FROM t_shirts t
LEFT JOIN discounts d ON t.t_shirt_id = d.t_shirt_id
GROUP BY t.brand
ORDER BY inventory_value DESC
LIMIT 1 OFFSET 1;""",
    },
    {
        "question": "Find t-shirts whose price is above the average price and stock is above the average stock.",
        "sql": """SELECT t_shirt_id, brand, price, stock_quantity
FROM t_shirts
WHERE price > (SELECT AVG(price) FROM t_shirts)
  AND stock_quantity > (SELECT AVG(stock_quantity) FROM t_shirts);""",
    },
    {
        "question": "For each brand, find the total number of products, total stock, average price and inventory value.",
        "sql": """SELECT brand,
       COUNT(*) AS product_count,
       SUM(stock_quantity) AS total_stock,
       AVG(price) AS average_price,
       SUM(price * stock_quantity) AS inventory_value
FROM t_shirts
GROUP BY brand
ORDER BY inventory_value DESC;""",
    },
    {
        "question": "Find the top 3 brands based on total discounted inventory value.",
        "sql": f"""SELECT t.brand, SUM({DISCOUNTED}) AS discounted_inventory_value
FROM t_shirts t
LEFT JOIN discounts d ON t.t_shirt_id = d.t_shirt_id
GROUP BY t.brand
ORDER BY discounted_inventory_value DESC
LIMIT 3;""",
    },
    {
        "question": "Find the color with the highest total stock quantity.",
        "sql": """SELECT color, SUM(stock_quantity) AS total_stock
FROM t_shirts
GROUP BY color
ORDER BY total_stock DESC
LIMIT 1;""",
    },
    {
        "question": "Find the brand with the highest total discount savings.",
        "sql": """SELECT t.brand,
       SUM(t.price * t.stock_quantity * COALESCE(d.pct_discount, 0) / 100) AS total_savings
FROM t_shirts t
JOIN discounts d ON t.t_shirt_id = d.t_shirt_id
GROUP BY t.brand
ORDER BY total_savings DESC
LIMIT 1;""",
    },
    {
        "question": "Find the t-shirts whose discounted price is higher than the average discounted price.",
        "sql": """SELECT t.t_shirt_id, t.brand, t.price, d.pct_discount,
       t.price * (1 - COALESCE(d.pct_discount, 0) / 100) AS discounted_price
FROM t_shirts t
LEFT JOIN discounts d ON t.t_shirt_id = d.t_shirt_id
WHERE t.price * (1 - COALESCE(d.pct_discount, 0) / 100) > (
    SELECT AVG(t2.price * (1 - COALESCE(d2.pct_discount, 0) / 100))
    FROM t_shirts t2
    LEFT JOIN discounts d2 ON t2.t_shirt_id = d2.t_shirt_id
);""",
    },
]
"""Structured database tools used by the AI assistants.

Every tool reads only from SQLite and returns JSON-serializable data, which
keeps the assistant grounded in the demo catalog and analytics tables.
"""

from __future__ import annotations

import json
from typing import Any

from .db import fetch_all, fetch_one


def _parse_features(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        value = json.loads(raw)
        return value if isinstance(value, list) else []
    except json.JSONDecodeError:
        return []


def _product_sql(select_fields: str = "*") -> str:
    return f"SELECT {select_fields} FROM Products"


def search_products(query: str | None = None, category: str | None = None, budget: float | None = None, limit: int = 8) -> dict[str, Any]:
    filters = ["1 = 1"]
    params: list[object] = []
    if query:
        filters.append("(LOWER(name) LIKE ? OR LOWER(description) LIKE ? OR LOWER(brand) LIKE ?)")
        token = f"%{query.lower()}%"
        params.extend([token, token, token])
    if category:
        filters.append("LOWER(category) = ?")
        params.append(category.lower())
    if budget is not None:
        filters.append("price <= ?")
        params.append(budget)

    params.append(limit)
    rows = fetch_all(
        f"""
        SELECT id, name, description, category, price, stock, rating, brand, features, image
        FROM Products
        WHERE {' AND '.join(filters)}
        ORDER BY rating DESC, price ASC
        LIMIT ?
        """,
        tuple(params),
    )
    products = [{**row, "features": _parse_features(row.get("features"))} for row in rows]
    return {"results": products, "count": len(products)}


def get_product(product_id: int) -> dict[str, Any]:
    row = fetch_one(
        """
        SELECT id, name, description, category, price, stock, rating, brand, features, image
        FROM Products
        WHERE id = ?
        """,
        (product_id,),
    )
    if not row:
        return {"product": None}

    reviews = fetch_all(
        """
        SELECT id, product_id, rating, comment
        FROM Reviews
        WHERE product_id = ?
        ORDER BY id DESC
        LIMIT 6
        """,
        (product_id,),
    )
    related = fetch_all(
        """
        SELECT id, name, description, category, price, stock, rating, brand, features, image
        FROM Products
        WHERE category = ? AND id != ?
        ORDER BY rating DESC, price ASC
        LIMIT 4
        """,
        (row["category"], product_id),
    )
    product = {**row, "features": _parse_features(row.get("features"))}
    return {
        "product": product,
        "reviews": reviews,
        "related_products": [{**item, "features": _parse_features(item.get("features"))} for item in related],
    }


def compare_products(product_ids: list[int]) -> dict[str, Any]:
    if not product_ids:
        return {"products": []}
    placeholders = ",".join(["?"] * len(product_ids))
    rows = fetch_all(
        f"""
        SELECT id, name, description, category, price, stock, rating, brand, features, image
        FROM Products
        WHERE id IN ({placeholders})
        ORDER BY rating DESC, price ASC
        """,
        tuple(product_ids),
    )
    return {"products": [{**row, "features": _parse_features(row.get("features"))} for row in rows]}


def list_categories() -> dict[str, Any]:
    rows = fetch_all(
        """
        SELECT category, COUNT(*) AS product_count, ROUND(AVG(price), 2) AS avg_price
        FROM Products
        GROUP BY category
        ORDER BY category
        """
    )
    return {"categories": rows}


def get_sales() -> dict[str, Any]:
    rows = fetch_all(
        """
        SELECT strftime('%Y-%m', created_at) AS month, ROUND(SUM(price), 2) AS revenue, COUNT(*) AS orders
        FROM Orders
        GROUP BY month
        ORDER BY month
        """
    )
    return {"sales": rows}


def get_recent_sales(days: int = 7) -> dict[str, Any]:
    rows = fetch_one(
        """
        SELECT COUNT(*) AS orders, ROUND(COALESCE(SUM(price), 0), 2) AS revenue
        FROM Orders
        WHERE datetime(created_at) >= datetime('now', ?)
        """,
        (f"-{days} days",),
    ) or {"orders": 0, "revenue": 0}
    return {"period_days": days, "summary": rows}


def get_orders(limit: int = 20) -> dict[str, Any]:
    rows = fetch_all(
        """
        SELECT o.id, o.product_id, p.name AS product_name, o.quantity, o.price, o.created_at
        FROM Orders o
        JOIN Products p ON p.id = o.product_id
        ORDER BY o.created_at DESC
        LIMIT ?
        """,
        (limit,),
    )
    return {"orders": rows}


def get_inventory() -> dict[str, Any]:
    rows = fetch_all(
        """
        SELECT id, name, category, stock, rating, brand, price
        FROM Products
        ORDER BY stock ASC, rating DESC
        """
    )
    return {
        "inventory": rows,
        "low_stock": [row for row in rows if int(row["stock"]) <= 15],
    }


def get_reviews(limit: int = 25) -> dict[str, Any]:
    rows = fetch_all(
        """
        SELECT r.id, r.product_id, p.name AS product_name, p.category, r.rating, r.comment
        FROM Reviews r
        JOIN Products p ON p.id = r.product_id
        ORDER BY r.rating ASC, r.id DESC
        LIMIT ?
        """,
        (limit,),
    )
    return {"reviews": rows}


def analytics_summary() -> dict[str, Any]:
    revenue_and_orders = fetch_one(
        """
        SELECT ROUND(COALESCE(SUM(price), 0), 2) AS revenue, COUNT(*) AS orders
        FROM Orders
        """
    ) or {"revenue": 0, "orders": 0}
    customers = fetch_one("SELECT COUNT(*) AS customers FROM Customers") or {"customers": 0}
    average_rating = fetch_one("SELECT ROUND(COALESCE(AVG(rating), 0), 2) AS average_rating FROM Products") or {"average_rating": 0}
    inventory = fetch_one("SELECT COALESCE(SUM(stock), 0) AS inventory FROM Products") or {"inventory": 0}

    overview = {
        "revenue": revenue_and_orders["revenue"],
        "orders": revenue_and_orders["orders"],
        "customers": customers["customers"],
        "average_rating": average_rating["average_rating"],
        "inventory": inventory["inventory"],
    }

    return {
        "overview": overview,
        "category_revenue": fetch_all(
            """
            SELECT p.category, ROUND(SUM(o.price), 2) AS revenue
            FROM Orders o
            JOIN Products p ON p.id = o.product_id
            GROUP BY p.category
            ORDER BY revenue DESC
            """
        ),
        "top_products": fetch_all(
            """
            SELECT p.id, p.name, ROUND(SUM(o.price), 2) AS revenue, SUM(o.quantity) AS units_sold
            FROM Orders o
            JOIN Products p ON p.id = o.product_id
            GROUP BY p.id
            ORDER BY revenue DESC
            LIMIT 6
            """
        ),
        "low_stock": fetch_all(
            """
            SELECT id, name, category, stock, price, rating, brand
            FROM Products
            WHERE stock <= 15
            ORDER BY stock ASC, rating DESC
            """
        ),
        "bad_reviews": fetch_all(
            """
            SELECT p.id, p.name, ROUND(AVG(r.rating), 2) AS avg_rating, COUNT(r.id) AS review_count
            FROM Reviews r
            JOIN Products p ON p.id = r.product_id
            GROUP BY p.id
            HAVING avg_rating < 4.2
            ORDER BY avg_rating ASC, review_count DESC
            """
        ),
        "sales_by_month": get_sales()["sales"],
    }

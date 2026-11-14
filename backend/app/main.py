"""FastAPI application entry point for the demo e-commerce backend."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .ai import answer_admin, answer_customer
from .db import fetch_all, fetch_one, init_database
from .models import AnalyticsResponse, ChatRequest, ChatResponse, DashboardResponse, ProductDetail, ProductSummary
from .tools import analytics_summary, get_inventory, get_orders, get_reviews, get_sales

app = FastAPI(title="AI Commerce Demo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _parse_features(raw: str | list[str] | None) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        import json

        try:
            value = json.loads(raw)
            return value if isinstance(value, list) else []
        except json.JSONDecodeError:
            return []
    return []


@app.on_event("startup")
def on_startup() -> None:
    init_database()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/products", response_model=list[ProductSummary])
def products(search: str | None = None, category: str | None = None, limit: int = 50) -> list[dict[str, object]]:
    filters = ["1 = 1"]
    params: list[object] = []
    if search:
        token = f"%{search.lower()}%"
        filters.append("(LOWER(name) LIKE ? OR LOWER(description) LIKE ? OR LOWER(brand) LIKE ?)")
        params.extend([token, token, token])
    if category:
        filters.append("LOWER(category) = ?")
        params.append(category.lower())
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
    return [{**row, "features": _parse_features(row.get("features"))} for row in rows]


@app.get("/products/{product_id}", response_model=ProductDetail)
def product_detail(product_id: int) -> dict[str, object]:
    row = fetch_one(
        """
        SELECT id, name, description, category, price, stock, rating, brand, features, image
        FROM Products
        WHERE id = ?
        """,
        (product_id,),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    row = {**row, "features": _parse_features(row.get("features"))}
    reviews = fetch_all(
        """
        SELECT id, product_id, rating, comment
        FROM Reviews
        WHERE product_id = ?
        ORDER BY rating DESC, id DESC
        LIMIT 8
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
    return {**row, "reviews": reviews, "related_products": [{**item, "features": _parse_features(item.get("features"))} for item in related]}


@app.get("/dashboard", response_model=DashboardResponse)
def dashboard() -> dict[str, object]:
    summary = analytics_summary()
    inventory = get_inventory()["inventory"]
    return {
        "overview": summary["overview"],
        "sales_by_month": summary["sales_by_month"],
        "revenue_by_category": summary["category_revenue"],
        "top_products": summary["top_products"],
        "stock_levels": inventory[:12],
        "low_stock_products": summary["low_stock"],
        "recent_orders": get_orders(limit=6)["orders"],
        "bad_review_products": summary["bad_reviews"],
        "analytics_summary": summary,
    }


@app.get("/analytics", response_model=AnalyticsResponse)
def analytics() -> dict[str, object]:
    summary = analytics_summary()
    inventory = get_inventory()
    review_rows = get_reviews(limit=20)["reviews"]
    return {
        "monthly_sales": summary["sales_by_month"],
        "category_revenue": summary["category_revenue"],
        "inventory_snapshot": inventory["inventory"],
        "review_summary": review_rows,
        "top_products": summary["top_products"],
        "summary": summary["overview"],
    }


@app.post("/chat/customer", response_model=ChatResponse)
def customer_chat(payload: ChatRequest) -> dict[str, object]:
    history = [message.model_dump() for message in payload.history]
    answer, tool_results = answer_customer(payload.message, history)
    return {"answer": answer, "tool_results": tool_results}


@app.post("/chat/admin", response_model=ChatResponse)
def admin_chat(payload: ChatRequest) -> dict[str, object]:
    history = [message.model_dump() for message in payload.history]
    answer, tool_results = answer_admin(payload.message, history)
    return {"answer": answer, "tool_results": tool_results}

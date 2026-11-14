"""AI orchestration for the customer and admin chat experiences.

The assistants are intentionally constrained to database-backed tools only. If an
API key is unavailable, the code falls back to deterministic tool-based answers
so the demo still works locally.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Callable

from openai import OpenAI

from .config import get_ai_config
from .tools import (
    analytics_summary,
    compare_products,
    get_inventory,
    get_orders,
    get_product,
    get_reviews,
    get_recent_sales,
    get_sales,
    list_categories,
    search_products,
)

ToolFn = Callable[..., dict[str, Any]]


CUSTOMER_TOOL_MAP: dict[str, ToolFn] = {
    "search_products": search_products,
    "get_product": get_product,
    "compare_products": compare_products,
    "list_categories": list_categories,
}

ADMIN_TOOL_MAP: dict[str, ToolFn] = {
    "get_sales": get_sales,
    "get_recent_sales": get_recent_sales,
    "get_orders": get_orders,
    "get_inventory": get_inventory,
    "get_reviews": get_reviews,
    "analytics_summary": analytics_summary,
}

TOOL_SCHEMAS = {
    "search_products": {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search the product catalog using only SQLite-backed data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": ["string", "null"]},
                    "category": {"type": ["string", "null"]},
                    "budget": {"type": ["number", "null"]},
                    "limit": {"type": "integer", "default": 8},
                },
                "additionalProperties": False,
            },
        },
    },
    "get_product": {
        "type": "function",
        "function": {
            "name": "get_product",
            "description": "Fetch a single product by id, including reviews and related products.",
            "parameters": {
                "type": "object",
                "properties": {"product_id": {"type": "integer"}},
                "required": ["product_id"],
                "additionalProperties": False,
            },
        },
    },
    "compare_products": {
        "type": "function",
        "function": {
            "name": "compare_products",
            "description": "Compare multiple products by id using only catalog data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_ids": {"type": "array", "items": {"type": "integer"}, "minItems": 2},
                },
                "required": ["product_ids"],
                "additionalProperties": False,
            },
        },
    },
    "list_categories": {
        "type": "function",
        "function": {
            "name": "list_categories",
            "description": "List product categories and counts from the SQLite catalog.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    "get_sales": {
        "type": "function",
        "function": {
            "name": "get_sales",
            "description": "Fetch monthly sales data from SQLite orders.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    "get_recent_sales": {
        "type": "function",
        "function": {
            "name": "get_recent_sales",
            "description": "Fetch revenue and order count for the most recent N days from SQLite.",
            "parameters": {
                "type": "object",
                "properties": {"days": {"type": "integer", "default": 7}},
                "additionalProperties": False,
            },
        },
    },
    "get_orders": {
        "type": "function",
        "function": {
            "name": "get_orders",
            "description": "Fetch recent orders from SQLite.",
            "parameters": {
                "type": "object",
                "properties": {"limit": {"type": "integer", "default": 20}},
                "additionalProperties": False,
            },
        },
    },
    "get_inventory": {
        "type": "function",
        "function": {
            "name": "get_inventory",
            "description": "Fetch the inventory snapshot and low-stock products from SQLite.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    "get_reviews": {
        "type": "function",
        "function": {
            "name": "get_reviews",
            "description": "Fetch reviews from SQLite.",
            "parameters": {
                "type": "object",
                "properties": {"limit": {"type": "integer", "default": 25}},
                "additionalProperties": False,
            },
        },
    },
    "analytics_summary": {
        "type": "function",
        "function": {
            "name": "analytics_summary",
            "description": "Fetch the current aggregate analytics summary from SQLite.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
}


CUSTOMER_SYSTEM_PROMPT = """You are a shopping assistant for a demo e-commerce site.
Only answer with facts that come from the tool results or the SQLite database.
Do not invent products, specifications, or policies.
If the database does not contain the answer, say so clearly and suggest a database-backed alternative.
Use tools whenever product search, comparison, categories, budget filtering, or specification lookup is needed.
"""

ADMIN_SYSTEM_PROMPT = """You are an internal ecommerce analytics assistant.
Only answer using SQLite-backed tool results.
Do not guess or make up business metrics.
If the data is incomplete, explain the gap and what can be queried next.
Focus on sales, inventory, products, reviews, trends, and restock guidance.
"""


def _extract_ints(text: str) -> list[int]:
    return [int(value) for value in re.findall(r"\b\d+\b", text)]


def _extract_budget(text: str) -> float | None:
    match = re.search(r"(?:under|below|budget of|budget|<=)\s*\$?(\d+(?:\.\d+)?)", text.lower())
    if match:
        return float(match.group(1))
    return None


def _extract_category(message: str) -> str | None:
    lowered = message.lower()
    category_map = {
        "laptop": "Laptops",
        "notebook": "Laptops",
        "phone": "Smartphones",
        "smartphone": "Smartphones",
        "headphone": "Headphones",
        "earbud": "Headphones",
        "watch": "Smart Watches",
        "camera": "Cameras",
        "gaming": "Gaming",
        "console": "Gaming",
        "vr": "Gaming",
    }
    for keyword, category in category_map.items():
        if keyword in lowered:
            return category
    return None


def _infer_customer_tools(message: str) -> list[tuple[str, dict[str, Any]]]:
    lowered = message.lower()
    budget = _extract_budget(message)
    category = _extract_category(message)
    product_ids = _extract_ints(message)
    tools: list[tuple[str, dict[str, Any]]] = []

    if any(term in lowered for term in ["compare", "vs", "versus", "difference between"]):
        if len(product_ids) >= 2:
            tools.append(("compare_products", {"product_ids": product_ids[:4]}))
    elif any(term in lowered for term in ["category", "categories"]):
        tools.append(("list_categories", {}))
    elif any(term in lowered for term in ["budget", "under", "affordable", "cheap", "recommend", "suggest", "find"]):
        inferred_query = None if category else message
        tools.append(
            (
                "search_products",
                {
                    "query": inferred_query,
                    "category": category,
                    "budget": budget,
                    "limit": 8,
                },
            )
        )
    if not tools:
        inferred_query = None if category else message
        tools.append(("search_products", {"query": inferred_query, "category": category, "budget": budget, "limit": 8}))
    return tools


def _infer_admin_tools(message: str) -> list[tuple[str, dict[str, Any]]]:
    lowered = message.lower()
    if any(term in lowered for term in ["last week", "past week", "this week", "weekly", "7 days"]):
        return [("get_recent_sales", {"days": 7})]
    if any(term in lowered for term in ["best-selling", "best selling", "top products", "best sellers", "best seller"]):
        return [("analytics_summary", {})]
    if any(term in lowered for term in ["revenue", "sales", "trends", "summary"]):
        return [("analytics_summary", {}), ("get_sales", {})]
    if any(term in lowered for term in ["low stock", "restock", "inventory", "stock"]):
        return [("get_inventory", {})]
    if any(term in lowered for term in ["reviews", "bad review", "negative"]):
        return [("get_reviews", {}), ("analytics_summary", {})]
    return [("analytics_summary", {}), ("get_orders", {})]


def _format_customer_fallback(message: str, results: list[dict[str, Any]]) -> str:
    if not results:
        return "I could not find matching products in the SQLite catalog. Try a broader search term, another category, or a larger budget."
    first = results[0]
    if "categories" in first:
        categories = ", ".join(f"{row['category']} ({row['product_count']})" for row in first["categories"])
        return f"The catalog currently includes: {categories}."
    if "products" in first:
        products = first["products"]
    elif "results" in first:
        products = first["results"]
    else:
        products = []
    if not products:
        return "No matching products were found in the database."
    lines = ["Here are the strongest database matches:"]
    for product in products[:5]:
        lines.append(f"- {product['name']} · ${product['price']:.0f} · rating {product['rating']}")
    return "\n".join(lines)


def _format_customer_answer(message: str, results: list[dict[str, Any]]) -> str:
    if not results:
        return _format_customer_fallback(message, results)

    first = results[0]
    if first.get("tool") == "list_categories":
        categories = first.get("result", {}).get("categories", [])
        if not categories:
            return "No categories were returned from the SQLite catalog."
        return "Available categories: " + ", ".join(f"{row['category']} ({row['product_count']})" for row in categories)

    if first.get("tool") == "compare_products":
        products = first.get("result", {}).get("products", [])
        if not products:
            return "I could not compare those product IDs because they were not found in the SQLite catalog."
        lines = ["Comparison based on SQLite data:"]
        for product in products:
            lines.append(f"- {product['name']} · ${product['price']:.0f} · rating {product['rating']} · {product['brand']}")
        return "\n".join(lines)

    if first.get("tool") == "get_product":
        product = first.get("result", {}).get("product")
        if not product:
            return "That product was not found in the SQLite catalog."
        features = ", ".join(product.get("features", [])[:5])
        return f"{product['name']} costs ${product['price']:.0f}, has a {product['rating']} rating, and features {features}."

    search_result = first.get("result", {})
    products = search_result.get("results", [])
    if not products:
        category = _extract_category(message)
        if category:
          return f"No matching {category.lower()} were found in the database for that budget."
        return "No matching products were found in the database."

    lines = ["Here are the best SQLite-backed matches:"]
    for product in products[:5]:
        lines.append(f"- {product['name']} · ${product['price']:.0f} · rating {product['rating']} · {product['brand']}")
    return "\n".join(lines)


def _format_admin_answer(message: str, results: list[dict[str, Any]]) -> str:
    if not results:
        return _format_admin_fallback(results)

    lowered = message.lower()
    summary_result = next((entry.get("result", {}) for entry in results if entry.get("tool") == "analytics_summary"), None)
    recent_sales_result = next((entry.get("result", {}) for entry in results if entry.get("tool") == "get_recent_sales"), None)
    inventory_result = next((entry.get("result", {}) for entry in results if entry.get("tool") == "get_inventory"), None)
    reviews_result = next((entry.get("result", {}) for entry in results if entry.get("tool") == "get_reviews"), None)

    if recent_sales_result:
        summary = recent_sales_result.get("summary", {})
        return f"SQLite shows ${summary.get('revenue', 0):,.2f} revenue across {summary.get('orders', 0)} orders in the last {recent_sales_result.get('period_days', 7)} days."

    if "best" in lowered and summary_result:
        top_products = summary_result.get("top_products", [])
        if top_products:
            lines = ["Best-selling products from SQLite:"]
            for product in top_products[:5]:
                lines.append(f"- {product['name']} · ${product['revenue']:.0f} revenue · {product['units_sold']} units")
            return "\n".join(lines)

    if any(term in lowered for term in ["low stock", "restock", "inventory", "stock"]):
        low_stock = (inventory_result or summary_result or {}).get("low_stock", [])
        if low_stock:
            lines = ["Low-stock products from SQLite:"]
            for product in low_stock[:10]:
                lines.append(f"- {product['name']} · {product['stock']} left · {product['category']}")
            return "\n".join(lines)

    if any(term in lowered for term in ["reviews", "bad review", "negative"]):
        bad_reviews = (summary_result or {}).get("bad_reviews", [])
        if bad_reviews:
            lines = ["Products with weaker review performance:"]
            for product in bad_reviews[:10]:
                lines.append(f"- {product['name']} · rating {product['avg_rating']} · {product['review_count']} reviews")
            return "\n".join(lines)

    if summary_result:
        overview = summary_result.get("overview", {})
        return (
            f"SQLite shows ${overview.get('revenue', 0):,.2f} revenue across {overview.get('orders', 0)} orders from {overview.get('customers', 0)} customers. "
            f"Average rating is {overview.get('average_rating', 0)}. Inventory totals {overview.get('inventory', 0)} units."
        )

    if reviews_result:
        reviews = reviews_result.get("reviews", [])
        return f"SQLite returned {len(reviews)} review records."

    return _format_admin_fallback(results)


def _format_admin_fallback(results: list[dict[str, Any]]) -> str:
    if not results:
        return "No database-backed analytics were returned."
    summary = results[0]
    if "period_days" in summary and "summary" in summary:
        period = summary.get("period_days", 7)
        inner = summary.get("summary", {})
        revenue = inner.get("revenue", 0)
        orders = inner.get("orders", 0)
        return f"SQLite shows ${revenue:,.2f} revenue across {orders} orders in the last {period} days."

    overview = summary.get("overview", {})
    revenue = overview.get("revenue", 0)
    orders = overview.get("orders", 0)
    customers = overview.get("customers", 0)
    inventory = overview.get("inventory", 0)
    average_rating = overview.get("average_rating", 0)
    low_stock = summary.get("low_stock", [])
    top_products = summary.get("top_products", [])
    return (
        f"SQLite shows ${revenue:,.0f} revenue across {orders} orders from {customers} customers. "
        f"Average rating is {average_rating}. Inventory totals {inventory} units. "
        f"Top products include {', '.join(item['name'] for item in top_products[:3]) or 'none listed'}. "
        f"Low-stock items: {', '.join(item['name'] for item in low_stock[:5]) or 'none'}.")


def _call_openai_tool_agent(system_prompt: str, messages: list[dict[str, Any]], tool_map: dict[str, ToolFn], tool_schemas: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    config = get_ai_config()
    if not config.api_key:
        raise RuntimeError("No API key configured")

    client = OpenAI(api_key=config.api_key, base_url=config.base_url)
    conversation = [{"role": "system", "content": system_prompt}] + messages
    tool_results: list[dict[str, Any]] = []

    for _ in range(4):
        response = client.chat.completions.create(
            model=config.model,
            messages=conversation,
            tools=tool_schemas,
            tool_choice="auto",
            temperature=0.2,
        )
        choice = response.choices[0].message
        if choice.tool_calls:
            conversation.append(choice.model_dump(exclude_none=True))
            for tool_call in choice.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments or "{}")
                tool_result = tool_map[tool_name](**tool_args)
                tool_results.append({"tool": tool_name, "arguments": tool_args, "result": tool_result})
                conversation.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result),
                    }
                )
            continue
        return choice.content or "", tool_results

    final = client.chat.completions.create(
        model=config.model,
        messages=conversation,
        temperature=0.2,
    )
    return final.choices[0].message.content or "", tool_results


def _tool_first_fallback(message: str, tool_map: dict[str, ToolFn], tool_inferences: list[tuple[str, dict[str, Any]]], admin: bool = False) -> tuple[str, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    for tool_name, args in tool_inferences:
        result = tool_map[tool_name](**args)
        results.append({"tool": tool_name, "arguments": args, "result": result})

    if admin:
        return _format_admin_answer(message, results), results
    return _format_customer_answer(message, results), results


def answer_customer(message: str, history: list[dict[str, Any]] | None = None) -> tuple[str, list[dict[str, Any]]]:
    messages = list(history or []) + [{"role": "user", "content": message}]
    try:
        _, tool_results = _call_openai_tool_agent(CUSTOMER_SYSTEM_PROMPT, messages, CUSTOMER_TOOL_MAP, [TOOL_SCHEMAS[name] for name in CUSTOMER_TOOL_MAP])
        return _format_customer_answer(message, tool_results), tool_results
    except Exception:
        return _tool_first_fallback(message, CUSTOMER_TOOL_MAP, _infer_customer_tools(message), admin=False)


def answer_admin(message: str, history: list[dict[str, Any]] | None = None) -> tuple[str, list[dict[str, Any]]]:
    messages = list(history or []) + [{"role": "user", "content": message}]
    try:
        _, tool_results = _call_openai_tool_agent(ADMIN_SYSTEM_PROMPT, messages, ADMIN_TOOL_MAP, [TOOL_SCHEMAS[name] for name in ADMIN_TOOL_MAP])
        return _format_admin_answer(message, tool_results), tool_results
    except Exception:
        return _tool_first_fallback(message, ADMIN_TOOL_MAP, _infer_admin_tools(message), admin=True)

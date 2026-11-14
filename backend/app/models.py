"""Pydantic schemas used by the API layer."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ProductSummary(BaseModel):
    id: int
    name: str
    description: str
    category: str
    price: float
    stock: int
    rating: float
    brand: str
    features: list[str]
    image: str


class ProductDetail(ProductSummary):
    reviews: list[dict[str, object]] = Field(default_factory=list)
    related_products: list[ProductSummary] = Field(default_factory=list)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    tool_results: list[dict[str, object]] = Field(default_factory=list)


class DashboardResponse(BaseModel):
    overview: dict[str, object]
    sales_by_month: list[dict[str, object]]
    revenue_by_category: list[dict[str, object]]
    top_products: list[dict[str, object]]
    stock_levels: list[dict[str, object]]
    low_stock_products: list[dict[str, object]]
    recent_orders: list[dict[str, object]]
    bad_review_products: list[dict[str, object]]
    analytics_summary: dict[str, object]


class AnalyticsResponse(BaseModel):
    monthly_sales: list[dict[str, object]]
    category_revenue: list[dict[str, object]]
    inventory_snapshot: list[dict[str, object]]
    review_summary: list[dict[str, object]]
    top_products: list[dict[str, object]]
    summary: dict[str, object]

"""Deterministic sample data generation for the SQLite demo database."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from random import Random

from .config import DB_PATH

IMAGE_PATH = "/images/product.jpg"

PRODUCT_GROUPS: dict[str, list[dict[str, object]]] = {
    "Laptops": [
        {"name": "AetherBook Pro 14", "brand": "Aether", "price": 1299, "stock": 18, "rating": 4.8, "description": "Thin-and-light creator laptop with a bright 14-inch panel and all-day battery life.", "features": ["14-inch OLED display", "Apple M2-style performance", "18-hour battery", "2.8K webcam", "1TB SSD"]},
        {"name": "Northwind Studio 16", "brand": "Northwind", "price": 1799, "stock": 11, "rating": 4.7, "description": "Workstation-class laptop tuned for design, editing, and AI-assisted workflows.", "features": ["16-inch 240Hz display", "RTX graphics", "32GB unified memory", "Thunderbolt 4", "Wi-Fi 7"]},
        {"name": "Orbit Flex 13", "brand": "Orbit", "price": 949, "stock": 24, "rating": 4.4, "description": "Convertible laptop for notes, streaming, and light productivity on the move.", "features": ["360-degree hinge", "Touch display", "Backlit keyboard", "16GB RAM", "512GB SSD"]},
        {"name": "Vertex Air 15", "brand": "Vertex", "price": 1149, "stock": 20, "rating": 4.6, "description": "Balanced everyday laptop with a premium finish and quiet thermals.", "features": ["15.3-inch panel", "Metal chassis", "Fast charge", "Dolby audio", "Fingerprint login"]},
        {"name": "PixelForge X17", "brand": "PixelForge", "price": 2199, "stock": 9, "rating": 4.9, "description": "High-end creator notebook with desktop-grade responsiveness and calibration support.", "features": ["17-inch mini-LED", "Color calibrated", "64GB RAM", "2TB SSD", "SD Express slot"]},
        {"name": "Nova Note 14", "brand": "Nova", "price": 799, "stock": 30, "rating": 4.2, "description": "Affordable student laptop with excellent portability and dependable battery life.", "features": ["12-hour battery", "Anti-glare display", "USB-C charging", "Fanless design", "256GB SSD"]},
        {"name": "Summit One 15", "brand": "Summit", "price": 1599, "stock": 14, "rating": 4.7, "description": "Premium business laptop with privacy controls and enterprise security features.", "features": ["IR camera", "Privacy shutter", "vPro class CPU", "Long battery", "Metal lid"]},
        {"name": "Halo Slim 13", "brand": "Halo", "price": 999, "stock": 22, "rating": 4.5, "description": "Ultra-portable laptop built for coffee shop workflows and frequent travel.", "features": ["13-inch display", "1.2kg chassis", "Fast wake", "Dual speakers", "512GB storage"]},
        {"name": "ForgeBook Studio 15", "brand": "Forge", "price": 1499, "stock": 12, "rating": 4.6, "description": "Creator-focused laptop with a strong GPU and color-rich display for media work.", "features": ["Dedicated graphics", "P3 color gamut", "32GB RAM", "Dual fans", "SD card reader"]},
    ],
    "Smartphones": [
        {"name": "Luma S24 Ultra", "brand": "Luma", "price": 1199, "stock": 28, "rating": 4.8, "description": "Flagship phone with a high-resolution camera stack and fluid display.", "features": ["6.8-inch AMOLED", "200MP camera", "5G", "Titanium frame", "5000mAh battery"]},
        {"name": "Pulse One", "brand": "Pulse", "price": 699, "stock": 35, "rating": 4.5, "description": "Smartphone that hits the sweet spot for performance, battery, and value.", "features": ["144Hz display", "Fast charging", "Dual stereo speakers", "128GB storage", "5G"]},
        {"name": "Astra Mini", "brand": "Astra", "price": 549, "stock": 42, "rating": 4.3, "description": "Compact smartphone with excellent one-handed usability and clean software.", "features": ["Compact form factor", "OLED display", "Night mode camera", "Wireless charging", "IP68"]},
        {"name": "Vertex X Pro", "brand": "Vertex", "price": 999, "stock": 19, "rating": 4.7, "description": "Creator-friendly phone with stabilized video capture and bright outdoor visibility.", "features": ["8K video", "Optical zoom", "ProRAW mode", "120Hz panel", "AI photo tools"]},
        {"name": "Orbit Neo", "brand": "Orbit", "price": 629, "stock": 31, "rating": 4.4, "description": "All-round smartphone designed for social, gaming, and multitasking.", "features": ["Dimensity-class chip", "256GB storage", "67W charging", "Stereo speakers", "Dual SIM"]},
        {"name": "Nova Edge", "brand": "Nova", "price": 879, "stock": 23, "rating": 4.6, "description": "Premium mid-range phone with a refined camera and polished industrial design.", "features": ["LTPO display", "Ultra-wide camera", "E-SIM support", "Face unlock", "Aluminum frame"]},
        {"name": "Halo Z Fold", "brand": "Halo", "price": 1499, "stock": 8, "rating": 4.5, "description": "Foldable smartphone for multitasking, reading, and showy demo moments.", "features": ["Foldable AMOLED", "Split-screen multitasking", "Stylus support", "Adaptive refresh", "Dual batteries"]},
        {"name": "Summit Lite", "brand": "Summit", "price": 449, "stock": 47, "rating": 4.1, "description": "Entry-level smartphone with dependable battery life and essential features.", "features": ["5000mAh battery", "Large display", "Face unlock", "Expandable storage", "USB-C"]},
        {"name": "PixelForge S", "brand": "PixelForge", "price": 1099, "stock": 16, "rating": 4.8, "description": "Photography-first smartphone tuned for sharp detail and natural skin tones.", "features": ["Large sensor camera", "Periscope zoom", "AI portrait mode", "120Hz display", "Fast wireless charging"]},
    ],
    "Headphones": [
        {"name": "AeroSound Max", "brand": "AeroSound", "price": 349, "stock": 29, "rating": 4.8, "description": "Luxury over-ear headphones with rich noise cancellation and plush comfort.", "features": ["Adaptive ANC", "40-hour battery", "Spatial audio", "Multipoint Bluetooth", "USB-C audio"]},
        {"name": "Pulse Buds Pro", "brand": "Pulse", "price": 199, "stock": 44, "rating": 4.5, "description": "Compact wireless earbuds with punchy bass and dependable call clarity.", "features": ["Wireless charging case", "Beamforming mics", "Transparency mode", "IPX4", "Fast pair"]},
        {"name": "Northwind Studio ANC", "brand": "Northwind", "price": 279, "stock": 17, "rating": 4.7, "description": "Over-ear headset for remote work, content creation, and long calls.", "features": ["Hybrid ANC", "40mm drivers", "Collapsible design", "30-hour battery", "Bluetooth 5.3"]},
        {"name": "Orbit Beat", "brand": "Orbit", "price": 129, "stock": 38, "rating": 4.3, "description": "Affordable headphones with energetic sound and a comfortable fit.", "features": ["On-ear design", "Quick charge", "Bass boost", "Fold-flat hinges", "Voice assistant"]},
        {"name": "Halo Quiet", "brand": "Halo", "price": 249, "stock": 21, "rating": 4.6, "description": "Travel-ready headphones that mute cabin noise and fold into a compact case.", "features": ["Travel case", "ANC", "40mm drivers", "USB-C charging", "Touch controls"]},
        {"name": "Vertex AirPods Maxx", "brand": "Vertex", "price": 379, "stock": 13, "rating": 4.9, "description": "Audiophile-leaning headphones with wide staging and premium materials.", "features": ["Wide soundstage", "Metal earcups", "Lossless support", "Auto pause", "Premium foam"]},
        {"name": "Summit Sport Earbuds", "brand": "Summit", "price": 119, "stock": 51, "rating": 4.2, "description": "Workout earbuds with secure fit and splash resistance for active users.", "features": ["Ear fins", "Sweat resistance", "Fast charge", "Mono mode", "Touch controls"]},
        {"name": "Forge DJ Pro", "brand": "Forge", "price": 229, "stock": 15, "rating": 4.4, "description": "Monitoring headphones for producers who want clean mids and punchy lows.", "features": ["Studio tuning", "Detachable cable", "Rotating earcups", "Closed-back design", "Durable build"]},
        {"name": "Nova Sleep Pods", "brand": "Nova", "price": 89, "stock": 33, "rating": 4.0, "description": "Tiny earbuds optimized for podcasts, sleep timers, and low-profile wear.", "features": ["Ultra-small shell", "Sleep mode", "Gentle fit", "Bluetooth 5.2", "Pocket case"]},
    ],
    "Smart Watches": [
        {"name": "Luma Watch Ultra", "brand": "Luma", "price": 499, "stock": 20, "rating": 4.8, "description": "High-end smartwatch with robust fitness tracking and premium case materials.", "features": ["ECG", "GPS", "Always-on display", "Water resistant", "Two-day battery"]},
        {"name": "Orbit Time 2", "brand": "Orbit", "price": 249, "stock": 36, "rating": 4.5, "description": "Balanced smartwatch for notifications, health tracking, and workouts.", "features": ["Heart rate tracking", "Sleep score", "GPS", "Swappable bands", "Fast charge"]},
        {"name": "Pulse Fit Mini", "brand": "Pulse", "price": 159, "stock": 41, "rating": 4.3, "description": "Lightweight fitness watch with great battery life and clean metrics.", "features": ["SpO2", "Run coaching", "5ATM", "14-day battery", "Workout zones"]},
        {"name": "Astra Loop", "brand": "Astra", "price": 189, "stock": 27, "rating": 4.4, "description": "Fashion-forward watch that still handles the essentials for active users.", "features": ["Metal case", "Crisp AMOLED", "Contacts sync", "Calendar alerts", "Women\'s health tracking"]},
        {"name": "Vertex Pulse Pro", "brand": "Vertex", "price": 329, "stock": 18, "rating": 4.7, "description": "Performance watch for outdoor training, hiking, and health monitoring.", "features": ["Dual-band GPS", "Altimeter", "Compass", "Training load", "Long battery"]},
        {"name": "Summit Daily", "brand": "Summit", "price": 129, "stock": 48, "rating": 4.1, "description": "Entry smartwatch for steps, messages, and everyday convenience.", "features": ["Notification mirroring", "Step counter", "Alarm", "Lightweight body", "USB magnetic charger"]},
        {"name": "Halo Trail Watch", "brand": "Halo", "price": 379, "stock": 12, "rating": 4.8, "description": "Rugged watch built for endurance athletes and outdoor expeditions.", "features": ["Rugged case", "Solar assist", "Topo maps", "Waterproof", "Multi-sport profiles"]},
        {"name": "Forge Classic Smart", "brand": "Forge", "price": 219, "stock": 24, "rating": 4.4, "description": "Traditional-looking smart watch with modern notifications and wellness metrics.", "features": ["Analog-inspired face", "Sleep tracking", "Payment support", "Voice assistant", "4-day battery"]},
        {"name": "Nova Flex Band", "brand": "Nova", "price": 99, "stock": 52, "rating": 4.0, "description": "Slim activity band for lightweight tracking without a bulky watch face.", "features": ["Slim band", "Step and calorie tracking", "Silent alarms", "7-day battery", "Color display"]},
    ],
    "Cameras": [
        {"name": "Aether Capture X", "brand": "Aether", "price": 1899, "stock": 10, "rating": 4.9, "description": "Versatile mirrorless camera with crisp autofocus and strong low-light performance.", "features": ["Full-frame sensor", "8K video", "In-body stabilization", "Dual card slots", "Flip screen"]},
        {"name": "PixelForge Z8", "brand": "PixelForge", "price": 1599, "stock": 14, "rating": 4.7, "description": "Creator camera with fast burst shooting and excellent color science.", "features": ["24MP sensor", "Eye AF", "4K 120fps", "Weather sealing", "USB-C charging"]},
        {"name": "Northwind Pocket Cam", "brand": "Northwind", "price": 699, "stock": 33, "rating": 4.4, "description": "Pocketable camera for travel vlogging and fast social uploads.", "features": ["1-inch sensor", "Stabilized video", "Built-in mic", "Flip-up screen", "Wi-Fi upload"]},
        {"name": "Orbit Flex Shot", "brand": "Orbit", "price": 999, "stock": 21, "rating": 4.6, "description": "Hybrid camera with helpful automation for casual shooters and families.", "features": ["Auto scene modes", "Optical zoom", "Bluetooth remote", "Photo burst", "Macro mode"]},
        {"name": "Summit Pro Lens Kit", "brand": "Summit", "price": 2499, "stock": 7, "rating": 4.8, "description": "Prosumer body bundled with a fast standard zoom for high-quality production.", "features": ["Kit lens included", "Dual stabilization", "10-bit color", "Log profiles", "Weather sealed"]},
        {"name": "Halo Snap Mini", "brand": "Halo", "price": 449, "stock": 40, "rating": 4.2, "description": "Instant camera for gifts, parties, and playful analog-style prints.", "features": ["Instant prints", "Selfie mirror", "Auto flash", "Fun filters", "USB charging"]},
        {"name": "Vertex Vision 7", "brand": "Vertex", "price": 1399, "stock": 17, "rating": 4.7, "description": "All-purpose hybrid camera ready for portraits, street, and video.", "features": ["Fast burst", "High ISO range", "Mic input", "Flip-out LCD", "Object tracking"]},
        {"name": "Nova Field 50", "brand": "Nova", "price": 899, "stock": 26, "rating": 4.5, "description": "Reliable camera for documentaries, events, and long-form YouTube shoots.", "features": ["Dual SD slots", "Long record time", "Clean HDMI", "Sturdy grip", "Touch focus"]},
        {"name": "Forge Retro 35", "brand": "Forge", "price": 579, "stock": 15, "rating": 4.3, "description": "Retro-styled camera that delivers tactile controls and pleasing images.", "features": ["Retro dials", "APSC sensor", "Film simulations", "Hybrid AF", "Metal body"]},
    ],
    "Gaming": [
        {"name": "Aether Blade 16", "brand": "Aether", "price": 2399, "stock": 8, "rating": 4.8, "description": "High-refresh gaming laptop with a premium chassis and strong thermal design.", "features": ["RTX 4070-class GPU", "240Hz display", "Mechanical keyboard", "32GB RAM", "RGB lighting"]},
        {"name": "Orbit PlayStation X", "brand": "Orbit", "price": 499, "stock": 25, "rating": 4.7, "description": "Next-gen console bundle built for big-screen gaming and couch co-op.", "features": ["4K output", "Quick resume", "DualSense-style controller", "1TB storage", "Tempest audio"]},
        {"name": "Vertex Rift VR", "brand": "Vertex", "price": 699, "stock": 13, "rating": 4.6, "description": "Standalone VR headset for immersive games, fitness, and demo experiences.", "features": ["Inside-out tracking", "High-resolution panels", "Hand tracking", "Wireless play", "Mixed reality"]},
        {"name": "Pulse Arena Mouse", "brand": "Pulse", "price": 89, "stock": 61, "rating": 4.4, "description": "Lightweight gaming mouse tuned for fast flicks and long sessions.", "features": ["26K DPI sensor", "Ultra-light shell", "Programmable buttons", "PTFE feet", "RGB zones"]},
        {"name": "Summit Key Pro", "brand": "Summit", "price": 149, "stock": 39, "rating": 4.5, "description": "Mechanical keyboard with hot-swap sockets and crisp gaming actuation.", "features": ["Hot-swappable switches", "Per-key RGB", "Aluminum top plate", "USB-C", "Sound dampening"]},
        {"name": "Halo Stream Deck", "brand": "Halo", "price": 179, "stock": 22, "rating": 4.3, "description": "Creator control pad for streamers, editors, and power users.", "features": ["LCD keys", "Custom profiles", "Macro support", "USB-C", "Compact stand"]},
        {"name": "Nova Elite Controller", "brand": "Nova", "price": 159, "stock": 34, "rating": 4.6, "description": "Premium controller with remappable inputs and a refined grip.", "features": ["Rear paddles", "Swappable sticks", "Low-latency wireless", "Profile switcher", "Charging dock"]},
        {"name": "Forge GameCapture 4K", "brand": "Forge", "price": 229, "stock": 18, "rating": 4.5, "description": "Capture card for streaming consoles and high-frame-rate PC content.", "features": ["4K passthrough", "Low latency", "USB 3.2", "HDR support", "OBS friendly"]},
        {"name": "Luma Arcade Monitor", "brand": "Luma", "price": 449, "stock": 14, "rating": 4.7, "description": "Fast gaming monitor with vibrant color and crisp motion handling.", "features": ["165Hz refresh", "1ms response", "QHD panel", "Adaptive sync", "Height adjustable"]},
    ],
}

CUSTOMER_NAMES = [
    "Maya Chen", "Jordan Patel", "Amir Hassan", "Sofia Rivera", "Nina Thompson",
    "Leo Martin", "Ava Johnson", "Daniel Kim", "Priya Shah", "Omar Diaz",
    "Hana Suzuki", "Noah Brown", "Elena Petrova", "Marcus Green", "Sara Ali",
    "Grace Lee", "Ibrahim Saleh", "Chloe Walker", "Ethan Wilson", "Fatima Noor",
    "Mila Novak", "Theo Clark", "Aiden Scott", "Zara Khan", "Lucas Miller",
    "Isabella Rossi", "Yusuf Kaya", "Emma Davis", "Arjun Menon", "Lina Haddad",
    "Ben Cooper", "Nadia Farouk", "Owen Turner", "Rania Malik", "Hugo Silva",
    "Layla Ahmed", "Mason Reed", "Yara Khalil", "Jack Evans", "Sana Rahman",
]

COUNTRIES = [
    "United States", "Canada", "United Kingdom", "Germany", "France", "United Arab Emirates",
    "Saudi Arabia", "India", "Singapore", "Australia", "Netherlands", "Spain",
]

REVIEW_TEMPLATES = [
    "Great everyday choice with excellent value.",
    "The build quality feels premium and reliable.",
    "Battery life is stronger than I expected.",
    "Fast, polished, and easy to recommend.",
    "A few minor quirks, but the overall experience is solid.",
    "Crisp screen, good feel, and dependable performance.",
    "Delivery and setup were smooth; product works as advertised.",
    "A smart buy for shoppers who want quality without overpaying.",
]


def _pick_comment(rng: Random, rating: float) -> str:
    if rating >= 4.7:
        return rng.choice([
            "Absolutely one of the best items in the catalog.",
            "Excellent finish, strong performance, and no real complaints.",
            "Feels premium and delivers exactly what it promises.",
        ])
    if rating >= 4.3:
        return rng.choice(REVIEW_TEMPLATES)
    return rng.choice([
        "Good idea, but it could be better on battery and polish.",
        "Fine for the price, though there are better alternatives.",
        "Usable and practical, but not a standout in this category.",
    ])


def _monthly_offsets() -> list[datetime]:
    now = datetime.now(timezone.utc)
    months = []
    for index in range(12):
        month_start = now - timedelta(days=30 * (11 - index))
        months.append(month_start)
    return months


def seed_database() -> None:
    """Create schema and seed demo content if the database is empty."""

    rng = Random(42)
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                rating REAL NOT NULL,
                brand TEXT NOT NULL,
                features TEXT NOT NULL,
                image TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES Products(id)
            );

            CREATE TABLE IF NOT EXISTS Customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                country TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                rating REAL NOT NULL,
                comment TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES Products(id)
            );
            """
        )

        product_count = cur.execute("SELECT COUNT(*) FROM Products").fetchone()[0]
        if product_count:
            return

        product_rows: list[tuple[object, ...]] = []
        for category, items in PRODUCT_GROUPS.items():
            for item in items:
                product_rows.append(
                    (
                        item["name"],
                        item["description"],
                        category,
                        float(item["price"]),
                        int(item["stock"]),
                        float(item["rating"]),
                        item["brand"],
                        json.dumps(item["features"]),
                        IMAGE_PATH,
                    )
                )

        cur.executemany(
            """
            INSERT INTO Products (name, description, category, price, stock, rating, brand, features, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            product_rows,
        )

        customers = []
        for index, name in enumerate(CUSTOMER_NAMES, start=1):
            customers.append(
                (
                    name,
                    f"customer{index:02d}@demo-store.com",
                    rng.choice(COUNTRIES),
                )
            )
        cur.executemany(
            "INSERT INTO Customers (name, email, country) VALUES (?, ?, ?)",
            customers,
        )

        products = cur.execute("SELECT id, price FROM Products").fetchall()
        months = _monthly_offsets()
        orders: list[tuple[object, ...]] = []
        for month_index, month_start in enumerate(months):
            order_count = 8 + month_index
            for _ in range(order_count):
                product_id, base_price = rng.choice(products)
                quantity = rng.randint(1, 4)
                unit_variation = rng.uniform(0.94, 1.06)
                line_total = round(base_price * quantity * unit_variation, 2)
                timestamp = month_start + timedelta(days=rng.randint(0, 27), hours=rng.randint(0, 23), minutes=rng.randint(0, 59))
                orders.append((int(product_id), quantity, line_total, timestamp.isoformat()))
        cur.executemany(
            "INSERT INTO Orders (product_id, quantity, price, created_at) VALUES (?, ?, ?, ?)",
            orders,
        )

        review_rows: list[tuple[object, ...]] = []
        for product_id, base_price in products:
            review_count = rng.randint(2, 5)
            product_rating = cur.execute("SELECT rating FROM Products WHERE id = ?", (product_id,)).fetchone()[0]
            for _ in range(review_count):
                rating = max(3.2, min(5.0, round(rng.normalvariate(product_rating, 0.35), 1)))
                review_rows.append((int(product_id), rating, _pick_comment(rng, rating)))
        cur.executemany(
            "INSERT INTO Reviews (product_id, rating, comment) VALUES (?, ?, ?)",
            review_rows,
        )

        conn.commit()

"""
Generate synthetic e-commerce dataset for the recommendation system.
Run this script once to create the CSV files used by the backend.
"""

import pandas as pd
import numpy as np
import random
import os

random.seed(42)
np.random.seed(42)

CATEGORIES = ["Electronics", "Books", "Clothing", "Home & Kitchen", "Sports", "Beauty", "Toys"]

PRODUCTS_RAW = [
    ("Wireless Noise-Cancelling Headphones", "Electronics",
     "Premium over-ear headphones with active noise cancellation, 30-hour battery life, Bluetooth 5.0, and foldable design. Perfect for travel and work-from-home setups.", 199.99),
    ("Mechanical Keyboard RGB", "Electronics",
     "Full-size mechanical keyboard with Cherry MX switches, per-key RGB lighting, aluminum frame, and USB-C detachable cable. Ideal for gamers and typists.", 129.99),
    ("Python Crash Course", "Books",
     "A hands-on, project-based introduction to programming in Python. Covers variables, lists, classes, and more through fun practical projects.", 29.99),
    ("The Pragmatic Programmer", "Books",
     "Classic software engineering book covering best practices, design patterns, and professional development tips for modern developers.", 39.99),
    ("Men's Running Shoes", "Sports",
     "Lightweight breathable running shoes with responsive foam midsole, durable rubber outsole, and reflective details for night runs.", 89.99),
    ("Yoga Mat Premium", "Sports",
     "6mm thick non-slip yoga mat made from eco-friendly TPE material. Includes carry strap and alignment lines. Great for yoga, pilates and stretching.", 49.99),
    ("Stainless Steel Water Bottle", "Home & Kitchen",
     "Insulated double-wall water bottle that keeps drinks cold 24 hours, hot 12 hours. BPA-free, leak-proof lid, fits most cup holders.", 24.99),
    ("Air Fryer 5.8 Qt", "Home & Kitchen",
     "Digital air fryer with 8 preset cooking functions, rapid air circulation technology, non-stick basket, and dishwasher-safe parts.", 89.99),
    ("Vitamin C Serum", "Beauty",
     "20% Vitamin C brightening serum with hyaluronic acid and vitamin E. Reduces dark spots, boosts collagen, and provides antioxidant protection.", 34.99),
    ("LEGO Architecture Set", "Toys",
     "Build iconic world landmarks with this 744-piece LEGO Architecture set. Includes detailed instructions and historical information about each structure.", 59.99),
    ("Smart Watch Fitness Tracker", "Electronics",
     "Advanced smartwatch with heart rate monitor, GPS, sleep tracking, SpO2 sensor, and 7-day battery. Water resistant to 50 meters.", 249.99),
    ("Wireless Earbuds True", "Electronics",
     "True wireless earbuds with active noise cancellation, 8-hour playtime (32 with case), IPX5 water resistance, and transparency mode.", 149.99),
    ("Clean Code", "Books",
     "A handbook of agile software craftsmanship by Robert C. Martin. Learn to write clean, readable, and maintainable code with practical examples.", 44.99),
    ("Atomic Habits", "Books",
     "James Clear's guide to building good habits and breaking bad ones. Uses scientific research and real-life stories to explain the 1% rule.", 19.99),
    ("Resistance Bands Set", "Sports",
     "Set of 5 resistance bands with different tension levels (10-50 lbs). Made from natural latex, includes carrying bag and exercise guide.", 19.99),
    ("Dumbbell Set Adjustable", "Sports",
     "Adjustable dumbbell set ranging from 5 to 52.5 lbs per dumbbell. Space-saving design with quick-adjust dial mechanism.", 299.99),
    ("Cast Iron Skillet 12\"", "Home & Kitchen",
     "Pre-seasoned cast iron skillet for use on stovetop, oven, and grill. Even heat distribution, naturally non-stick when properly maintained.", 39.99),
    ("Instant Pot Duo 7-in-1", "Home & Kitchen",
     "Multi-use programmable pressure cooker that replaces 7 kitchen appliances. 6-quart capacity, 14 smart programs, and safety features.", 79.99),
    ("Retinol Eye Cream", "Beauty",
     "Retinol and peptide eye cream that reduces fine lines, dark circles, and puffiness. Fragrance-free, dermatologist tested, suitable for sensitive skin.", 28.99),
    ("Skincare Set Complete", "Beauty",
     "Complete skincare routine set with cleanser, toner, serum, moisturizer, and SPF 50 sunscreen. Suitable for all skin types.", 79.99),
    ("Remote Control Car", "Toys",
     "High-speed remote control car with 2.4GHz technology, shock-absorbing suspension, and 30+ mph top speed. Includes rechargeable batteries.", 44.99),
    ("Board Game Strategy", "Toys",
     "Award-winning strategy board game for 2-4 players. Features resource management, territory control, and multiple paths to victory.", 54.99),
    ("4K Webcam Streaming", "Electronics",
     "4K ultra HD webcam with autofocus, built-in noise-cancelling microphone, privacy cover, and plug-and-play USB-C setup.", 99.99),
    ("Monitor Stand Ergonomic", "Electronics",
     "Adjustable monitor stand with full motion arm, cable management, USB hub, and 17.6 lb weight capacity. Fits screens up to 32\".", 69.99),
    ("The Design of Everyday Things", "Books",
     "Don Norman's classic book on user-centered design and human psychology. Essential reading for designers, engineers and product managers.", 24.99),
    ("Deep Work", "Books",
     "Cal Newport's guide to focused success in a distracted world. Provides strategies to maximize cognitive performance and professional value.", 17.99),
    ("Tennis Racket Pro", "Sports",
     "Graphite tennis racket with open string pattern for maximum spin and power. Includes protective cover and vibration dampener.", 79.99),
    ("Cycling Gloves Padded", "Sports",
     "Half-finger cycling gloves with gel padding, moisture-wicking fabric, touchscreen-compatible fingertips, and reflective details.", 24.99),
    ("Bamboo Cutting Board Set", "Home & Kitchen",
     "Set of 3 organic bamboo cutting boards in different sizes. Knife-friendly, antimicrobial, and easy to clean. Juice grooves on larger board.", 34.99),
    ("Coffee Grinder Burr", "Home & Kitchen",
     "Conical burr coffee grinder with 40 grind settings, 8-oz bean hopper, and removable grinding bowl. Consistent grind for any brewing method.", 49.99),
    ("Hyaluronic Acid Moisturizer", "Beauty",
     "Oil-free moisturizer with triple-weight hyaluronic acid for plumping hydration. Fragrance-free, non-comedogenic, and fast-absorbing.", 22.99),
    ("Natural Lip Balm Set", "Beauty",
     "Set of 8 tinted and clear organic lip balms with SPF 15. Made with beeswax, shea butter, and natural flavors. Zero plastic packaging.", 18.99),
    ("Puzzle 1000 Piece", "Toys",
     "1000-piece jigsaw puzzle featuring a vibrant world map design. Made from recycled materials with a smooth finish for easy handling.", 22.99),
    ("Science Kit Kids", "Toys",
     "STEM science kit with 30+ experiments covering chemistry, physics, and biology. Includes safe materials, goggles, and instruction booklet.", 39.99),
    ("Portable SSD 1TB", "Electronics",
     "Compact solid-state drive with 1050MB/s read speeds, USB 3.2 Gen 2 interface, hardware encryption, and shock-resistant casing.", 89.99),
    ("Smart LED Bulbs 4-Pack", "Electronics",
     "16 million color WiFi smart bulbs compatible with Alexa and Google Home. Schedule, dim, and change colors from your smartphone app.", 39.99),
    ("System Design Interview", "Books",
     "Comprehensive guide to ace system design interviews at top tech companies. Covers distributed systems, scalability, and architecture patterns.", 34.99),
    ("The Staff Engineer's Path", "Books",
     "Tanya Reilly's guide to technical leadership beyond the individual contributor track. Covers scope, influence, and career growth.", 39.99),
    ("Foam Roller Muscle", "Sports",
     "High-density foam roller for muscle recovery and myofascial release. 18-inch length, 6-inch diameter, supports up to 500 lbs.", 29.99),
    ("Protein Powder Whey", "Sports",
     "Whey protein isolate powder, 25g protein per serving, 5.5g BCAAs, low sugar, multiple flavors. NSF Certified for Sport.", 59.99),
    ("Dutch Oven 5.5 Qt", "Home & Kitchen",
     "Enameled cast iron Dutch oven perfect for braising, soups, stews, and bread baking. Oven safe to 500°F, dishwasher safe.", 89.99),
    ("Stand Mixer 5 Qt", "Home & Kitchen",
     "Tilt-head stand mixer with 10-speed settings and 5-quart stainless steel bowl. Includes flat beater, dough hook, and wire whip.", 249.99),
    ("Face Wash Gentle", "Beauty",
     "Gentle foaming face wash with ceramides and niacinamide. Removes makeup and impurities without stripping skin's natural moisture barrier.", 16.99),
    ("Sheet Mask Set 20", "Beauty",
     "Set of 20 Korean sheet masks in assorted varieties: brightening, hydrating, anti-aging, and soothing. Made with natural botanical extracts.", 29.99),
    ("LEGO Technic Set", "Toys",
     "Advanced LEGO Technic building set with 1,226 pieces. Features working mechanisms including steering and pistons. For ages 11+.", 79.99),
    ("Card Game Exploding", "Toys",
     "Highly strategic card game for 2-5 players. Each game lasts 15 minutes. Perfect for parties and family game nights.", 19.99),
]

NUM_USERS = 200
NUM_PRODUCTS = len(PRODUCTS_RAW)

# --- Users ---
first_names = ["Alice","Bob","Carol","David","Eve","Frank","Grace","Henry","Isla","Jack",
               "Karen","Leo","Mia","Noah","Olivia","Paul","Quinn","Rachel","Sam","Tina",
               "Uma","Victor","Wendy","Xander","Yara","Zoe","Aaron","Beth","Chris","Diana"]
last_names = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis",
              "Wilson","Moore","Taylor","Anderson","Thomas","Jackson","White","Harris","Martin"]

users = []
for i in range(1, NUM_USERS + 1):
    fn = random.choice(first_names)
    ln = random.choice(last_names)
    email = f"{fn.lower()}.{ln.lower()}{i}@example.com"
    users.append({"id": i, "name": f"{fn} {ln}", "email": email})

df_users = pd.DataFrame(users)

# --- Products ---
products = []
for i, (name, category, description, price) in enumerate(PRODUCTS_RAW, 1):
    products.append({
        "id": i,
        "name": name,
        "category": category,
        "description": description,
        "price": price,
        "image_url": f"https://picsum.photos/seed/{i+10}/400/300",
        "stock": random.randint(10, 200),
        "rating_avg": round(random.uniform(3.5, 5.0), 1),
    })

df_products = pd.DataFrame(products)

# --- Interactions (ratings) ---
# Simulate user preferences by category
user_category_prefs = {}
for uid in range(1, NUM_USERS + 1):
    prefs = random.sample(CATEGORIES, k=random.randint(2, 4))
    user_category_prefs[uid] = prefs

interactions = []
seen = set()
for uid in range(1, NUM_USERS + 1):
    prefs = user_category_prefs[uid]
    # How many products this user rated
    n_rated = random.randint(8, 25)
    # Pool: preferred categories get higher chance
    pool = []
    for p in products:
        if p["category"] in prefs:
            pool.extend([p["id"]] * 4)
        else:
            pool.append(p["id"])
    sampled_pids = list({random.choice(pool) for _ in range(n_rated * 3)})[:n_rated]
    for pid in sampled_pids:
        if (uid, pid) in seen:
            continue
        seen.add((uid, pid))
        # Preferred category → higher rating
        cat = next(p["category"] for p in products if p["id"] == pid)
        if cat in prefs:
            rating = round(random.triangular(3.5, 5.0, 4.5), 1)
        else:
            rating = round(random.triangular(1.5, 4.0, 2.5), 1)
        interactions.append({
            "user_id": uid,
            "product_id": pid,
            "rating": min(5.0, max(1.0, rating)),
            "interaction_type": random.choice(["view", "view", "view", "purchase", "click"]),
            "timestamp": pd.Timestamp("2024-01-01") + pd.Timedelta(days=random.randint(0, 450)),
        })

df_interactions = pd.DataFrame(interactions)

os.makedirs("backend/data", exist_ok=True)
df_users.to_csv("backend/data/users.csv", index=False)
df_products.to_csv("backend/data/products.csv", index=False)
df_interactions.to_csv("backend/data/interactions.csv", index=False)

print(f"✅ Generated {len(df_users)} users")
print(f"✅ Generated {len(df_products)} products")
print(f"✅ Generated {len(df_interactions)} interactions")
print(f"   Sparsity: {1 - len(df_interactions)/(NUM_USERS*NUM_PRODUCTS):.2%}")

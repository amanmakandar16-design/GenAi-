"""A small, explainable product recommender for a sample online shop.

Run `python recommend.py --demo` to see three evaluated profiles, or run
`python recommend.py` to enter preferences interactively.
"""

from dataclasses import dataclass
import re
import sys
from typing import Optional


@dataclass(frozen=True)
class Product:
    name: str
    category: str
    price: float
    description: str


PRODUCTS = [
    Product("TrailBlaze Running Shoes", "Sports", 79.99, "Lightweight running shoes with cushioned support for road and trail workouts."),
    Product("FlexFit Yoga Mat", "Sports", 29.99, "Non-slip, cushioned yoga mat for stretching, pilates, and home workouts."),
    Product("AeroFit Smartwatch", "Electronics", 119.99, "Tracks heart rate, steps, sleep, and GPS runs with a long battery life."),
    Product("SoundWave Wireless Headphones", "Electronics", 89.99, "Noise-isolating wireless headphones for music, travel, and focused work."),
    Product("Pocket Bluetooth Speaker", "Electronics", 39.99, "Portable, water-resistant speaker for music outdoors and at home."),
    Product("BrewMaster Coffee Maker", "Home", 64.99, "Programmable drip coffee maker with reusable filter for fresh morning coffee."),
    Product("LumiDesk LED Lamp", "Home", 34.99, "Adjustable desk lamp with dimmable light for reading, study, and office work."),
    Product("CloudRest Pillow", "Home", 44.99, "Supportive memory-foam pillow designed for comfortable, restful sleep."),
    Product("ChefPro Blender", "Home", 74.99, "Powerful kitchen blender for smoothies, soups, and meal preparation."),
    Product("UrbanLite Backpack", "Accessories", 49.99, "Water-resistant everyday backpack with a padded laptop sleeve and roomy storage."),
    Product("Voyager Carry-On", "Accessories", 129.99, "Lightweight wheeled cabin suitcase for business trips and weekend travel."),
    Product("PolarShield Water Bottle", "Sports", 24.99, "Insulated stainless-steel bottle that keeps drinks cold during hikes and workouts."),
    Product("Focus Mechanical Keyboard", "Electronics", 99.99, "Comfortable mechanical keyboard for programming, gaming, and desk productivity."),
    Product("PageTurn E-Reader", "Electronics", 139.99, "Glare-free e-reader with weeks of battery life for reading on the go."),
    Product("GardenGrow Starter Kit", "Home", 54.99, "Beginner indoor herb garden kit with planters, seeds, and a compact grow light."),
    Product("ComfyKnit Hoodie", "Clothing", 45.99, "Soft, warm everyday hoodie for casual wear, walks, and travel."),
    Product("SunShield Daypack", "Accessories", 35.99, "Compact lightweight daypack for sightseeing, school, and short hikes."),
]


def tokens(text: str) -> set[str]:
    """Normalize words and omit common filler terms for simple keyword matching."""
    stop_words = {"a", "an", "and", "at", "for", "in", "of", "on", "the", "to", "with", "my", "i", "need", "want", "use", "used"}
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if word not in stop_words and len(word) > 1}


def recommend(category: str, budget: Optional[float], intended_use: str, limit: int = 3):
    """Rank affordable products by category fit and intended-use keyword overlap."""
    use_words = tokens(intended_use)
    candidates = [p for p in PRODUCTS if budget is None or p.price <= budget]
    ranked = []
    for product in candidates:
        category_match = bool(category.strip()) and product.category.casefold() == category.strip().casefold()
        product_words = tokens(product.name + " " + product.description)
        matched = use_words & product_words
        # Category fit anchors results; keyword overlap distinguishes use cases.
        score = (3.0 if category_match else 0.0) + len(matched)
        ranked.append((score, len(matched), category_match, product, matched))

    ranked.sort(key=lambda row: (-row[0], -row[1], row[3].price, row[3].name))
    results = []
    for score, _, category_match, product, matched in ranked[:limit]:
        reasons = []
        if category_match:
            reasons.append(f"matches your {product.category} category")
        if matched:
            reasons.append("description matches: " + ", ".join(sorted(matched)))
        if budget is not None:
            reasons.append(f"costs ${product.price:.2f}, within your ${budget:.2f} budget")
        if not reasons:
            reasons.append("is among the closest available matches to your preferences")
        results.append((product, "; ".join(reasons)))
    return results


def show_recommendations(category: str, budget: Optional[float], intended_use: str) -> list[Product]:
    print(f"\nPreferences: category={category or 'any'}, budget={'any' if budget is None else f'${budget:.2f}'}, use={intended_use or 'not specified'}")
    results = recommend(category, budget, intended_use)
    if not results:
        print("No products fit that budget. Try increasing the budget.")
        return []
    for index, (product, reason) in enumerate(results, 1):
        print(f"{index}. {product.name} — {product.category} — ${product.price:.2f}")
        print(f"   {product.description}")
        print(f"   Why: {reason}.")
    return [product for product, _ in results]


def demo() -> None:
    profiles = [
        ("Runner", "Sports", 90, "running training road workout"),
        ("Remote worker", "Electronics", 105, "focused work at desk programming productivity"),
        ("Weekend traveler", "Accessories", 55, "travel hiking lightweight daypack"),
    ]
    print("SAMPLE PRODUCT RECOMMENDATIONS\n")
    for name, category, budget, use in profiles:
        print(f"--- {name} ---")
        picks = show_recommendations(category, budget, use)
        category_ok = sum(p.category.casefold() == category.casefold() for p in picks)
        budget_ok = sum(p.price <= budget for p in picks)
        keyword_hits = sum(bool(tokens(use) & tokens(p.name + " " + p.description)) for p in picks)
        print(f"Evaluation: {category_ok}/{len(picks)} match category; {budget_ok}/{len(picks)} fit budget; {keyword_hits}/{len(picks)} match at least one intended-use keyword.\n")


def interactive() -> None:
    print("AI-Assisted Product Recommendation System")
    print("Categories: " + ", ".join(sorted({p.category for p in PRODUCTS})))
    category = input("Preferred category (leave blank for any): ").strip()
    budget_text = input("Maximum budget in dollars (leave blank for no limit): ").strip()
    try:
        budget = float(budget_text) if budget_text else None
        if budget is not None and budget < 0:
            raise ValueError
    except ValueError:
        print("Please enter a non-negative number for the budget.")
        return
    intended_use = input("What will you use the product for? ").strip()
    show_recommendations(category, budget, intended_use)


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        interactive()

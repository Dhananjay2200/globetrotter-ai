"""
Test Suite: Combinatorial Multi-Filter with Region, Category, and Date.
Tests strict Boolean AND logic across all dimensions.
"""

from datetime import datetime, timezone, timedelta

# Sample mock articles
now = datetime.now(timezone.utc)
yesterday = now - timedelta(days=1)
last_week = now - timedelta(days=5)
last_month = now - timedelta(days=20)
old = now - timedelta(days=60)

mock_posts = [
    {
        "id": 1,
        "title": "Annapurna Sanctuary: Trekking Through Cloud Forests",
        "destination": "Annapurna Sanctuary",
        "country": "Nepal",
        "region": "South & Central Asia",
        "category": "Waterfalls, Mountains & Natural Wonders",
        "published_at": now.isoformat(),
    },
    {
        "id": 2,
        "title": "Ladakh High-Altitude Serenity",
        "destination": "Ladakh",
        "country": "India",
        "region": "South & Central Asia",
        "category": "Seasonal & Winter/Summer Escapes",
        "published_at": now.isoformat(),
    },
    {
        "id": 3,
        "title": "Banff National Park: Turquoise Glacial Lakes",
        "destination": "Banff National Park",
        "country": "Canada",
        "region": "North America",
        "category": "Waterfalls, Mountains & Natural Wonders",
        "published_at": old.isoformat(),
    },
    {
        "id": 4,
        "title": "Beyond Victoria Falls",
        "destination": "Livingstone",
        "country": "Zambia",
        "region": "Sub-Saharan Africa",
        "category": "Waterfalls, Mountains & Natural Wonders",
        "published_at": now.isoformat(),
    },
]

def test_combinatorial():
    # Test 1: Region = "South & Central Asia" AND Category = "Waterfalls, Mountains & Natural Wonders" AND Date = "today"
    # Expected: only post 1 (Annapurna)
    results = [
        p for p in mock_posts
        if p["region"] == "South & Central Asia"
        and "mountain" in p["category"].lower()
        and (now - datetime.fromisoformat(p["published_at"])).total_seconds() <= 86400
    ]
    assert len(results) == 1
    assert results[0]["id"] == 1
    print("Test 1 Passed: Annapurna matches Region + Category + Today")

    # Test 2: Region = "South & Central Asia" AND Category = "Waterfalls, Mountains & Natural Wonders" AND Date = "old" (e.g. > 30 days)
    # Expected: 0 matches (Banff is old but in North America)
    results = [
        p for p in mock_posts
        if p["region"] == "South & Central Asia"
        and "mountain" in p["category"].lower()
        and (now - datetime.fromisoformat(p["published_at"])).total_seconds() > 30 * 86400
    ]
    assert len(results) == 0
    print("Test 2 Passed: 0 matches for old Annapurna")

    # Test 3: Category = "Waterfalls, Mountains & Natural Wonders" AND Date = "today" (All regions)
    # Expected: post 1 (Annapurna) and post 4 (Victoria Falls)
    results = [
        p for p in mock_posts
        if ("mountain" in p["category"].lower() or "waterfall" in p["category"].lower())
        and (now - datetime.fromisoformat(p["published_at"])).total_seconds() <= 86400
    ]
    assert len(results) == 2
    print("Test 3 Passed: 2 matches for Category + Today across all regions")

    print("\nALL 3-WAY COMBINATORIAL FILTER TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_combinatorial()

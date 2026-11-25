"""
GlobeTrotter AI - Topic Discovery Service.
Discovers global tourism destinations and unique article angles using NVIDIA NIM.
"""

import json
import re
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.llm import get_chat_llm
from app.database.models import Topic, Destination
from app.utils.logging import logger
from langchain_core.messages import SystemMessage, HumanMessage


# Worldwide Tourism Categories according to GlobeTrotter AI requirements
TOURISM_CATEGORIES = [
    "Historical Monuments & Heritage Sites",
    "Waterfalls, Mountains & Natural Wonders",
    "Hidden Gems & Unexplored Places",
    "Festivals & Cultural Traditions",
    "Local Cuisines & Culinary Journeys",
    "Travel Experiences & Immersive Activities",
    "Road Trips & Scenic Itineraries",
    "Adventure Tourism & Extreme Expeditions",
    "Wildlife, Safaris & National Parks",
    "Ancient Civilizations & Historic Cities",
    "Seasonal & Winter/Summer Escapes",
    "Budget Travel & Backpacker Guides",
    "Coastal Escapes & Island Wonders",
]

# Geographic Regions
GLOBAL_REGIONS = [
    "East & Southeast Asia",
    "South & Central Asia",
    "Middle East & North Africa",
    "Sub-Saharan Africa",
    "Western & Northern Europe",
    "Southern & Eastern Europe",
    "North America",
    "Central America & Caribbean",
    "South America",
    "Oceania & Pacific Islands",
]


class TopicProposal(BaseModel):
    """Schema for a single discovered tourism topic."""
    destination: str = Field(..., description="Name of the tourist destination, city, or site")
    country: str = Field(..., description="Country where the destination is located")
    region: str = Field(..., description="Geographical or continent region")
    category: str = Field(..., description="One of the recognized tourism categories")
    proposed_title: str = Field(..., description="Compelling, SEO-friendly article title")
    unique_angle: str = Field(..., description="Distinct editorial perspective, focus, or theme")
    discovery_source: str = Field(default="ai_discovery", description="Topic source or discovery mode")


class TopicDiscoveryBatch(BaseModel):
    """Container for batch topic discovery."""
    topics: List[TopicProposal] = Field(default_factory=list)


def get_recent_destinations(db: Session, limit: int = 40) -> List[str]:
    """Retrieves names of recently covered destinations to prevent repetition."""
    try:
        destinations = (
            db.query(Topic.destination)
            .order_by(Topic.created_at.desc())
            .limit(limit)
            .all()
        )
        return list(set(d[0] for d in destinations if d[0]))
    except Exception as exc:
        logger.warning(f"Could not fetch recent destinations from DB: {exc}")
        return []


def clean_json_response(raw_text: str) -> str:
    """Strips markdown code blocks, reasoning traces, or preamble from LLM text."""
    text = raw_text.strip()
    # Remove markdown code fences if present
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1).strip()
    # Find JSON boundaries { ... } or [ ... ]
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        return text[start : end + 1]
    return text


def get_next_balanced_region_and_category(db: Session) -> tuple[str, str]:
    """
    Selects the next region and category to ensure 100% balanced worldwide coverage.
    Guarantees rotation across all 10 continents/regions and 13 tourism categories.
    """
    try:
        # Fetch recent topics
        recent_topics = db.query(Topic).order_by(Topic.created_at.desc()).limit(100).all()

        # Count category occurrences in recent history
        cat_counts = {cat: 0 for cat in TOURISM_CATEGORIES}
        for t in recent_topics:
            if t.category in cat_counts:
                cat_counts[t.category] += 1

        # Pick least represented category
        selected_category = min(TOURISM_CATEGORIES, key=lambda c: cat_counts[c])

        # Rotate regions sequentially based on total topics count for perfect round-robin global coverage
        total_count = db.query(Topic).count()
        selected_region = GLOBAL_REGIONS[total_count % len(GLOBAL_REGIONS)]

        return selected_region, selected_category
    except Exception as exc:
        logger.warning(f"Error determining balanced region/category: {exc}")
        return GLOBAL_REGIONS[0], TOURISM_CATEGORIES[0]


def discover_topics(
    db: Session,
    count: int = 5,
    target_region: Optional[str] = None,
    target_category: Optional[str] = None,
) -> List[TopicProposal]:
    """
    Discovers new worldwide tourism topics using the configured NVIDIA LLM.
    Enforces geographic diversity and avoids recently covered destinations.
    """
    recent_places = get_recent_destinations(db, limit=30)
    recent_exclusion_clause = (
        f"Do NOT generate topics for these recently covered destinations: {', '.join(recent_places[:20])}."
        if recent_places
        else "Ensure broad worldwide coverage across multiple continents."
    )

    region_clause = (
        f"Target Region: Focus exclusively on destinations within '{target_region}'."
        if target_region
        else "Target Region: Diverse mix across different continents (Asia, Europe, Americas, Africa, Oceania)."
    )

    category_clause = (
        f"Target Category: Focus on '{target_category}'."
        if target_category
        else f"Select diverse categories from: {', '.join(TOURISM_CATEGORIES[:8])}."
    )

    system_prompt = (
        "You are the Chief Travel Editor and Topic Discovery Intelligence for GlobeTrotter AI. "
        "Your mission is to discover captivating, fact-based tourism article topics worldwide.\n"
        "Requirements:\n"
        f"1. Generate exactly {count} distinct tourism topics.\n"
        "2. Cover genuine, visitable global destinations with cultural, historical, or natural significance.\n"
        "3. Provide a unique, specific editorial angle for each (e.g. 'off-season photography secrets', "
        "'indigenous culinary traditions', 'forgotten architectural wonders', 'responsible eco-trekking').\n"
        "4. Avoid generic angles like 'a comprehensive travel guide'. Make each angle fresh and intriguing.\n"
        f"5. {region_clause}\n"
        f"6. {category_clause}\n"
        f"7. {recent_exclusion_clause}\n\n"
        "OUTPUT FORMAT:\n"
        "You must respond with ONLY valid JSON adhering strictly to this JSON structure:\n"
        "{\n"
        '  "topics": [\n'
        "    {\n"
        '      "destination": "Name of destination",\n'
        '      "country": "Country name",\n'
        '      "region": "Geographical region",\n'
        '      "category": "Recognized category",\n'
        '      "proposed_title": "Engaging Article Title",\n'
        '      "unique_angle": "Distinct angle or focus (1-2 sentences)"\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    user_prompt = f"Discover {count} unique worldwide tourism topics right now."

    llm = get_chat_llm(temperature=0.7, max_tokens=2048)
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])
        raw_output = response.content
        cleaned_json = clean_json_response(raw_output)
        parsed_data = json.loads(cleaned_json)

        batch = TopicDiscoveryBatch.model_validate(parsed_data)
        logger.info(f"[+] Successfully discovered {len(batch.topics)} new tourism topics via NVIDIA NIM.")
        return batch.topics

    except json.JSONDecodeError as json_err:
        logger.error(f"Failed to parse LLM JSON response: {json_err}. Raw output preview: {raw_output[:200]}")
        raise ValueError(f"Invalid JSON returned by LLM: {json_err}")
    except Exception as exc:
        logger.error(f"Error during topic discovery: {exc}")
        raise

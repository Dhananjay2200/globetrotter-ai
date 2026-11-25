"""
GlobeTrotter AI - SEO Optimization Service.
Generates search-engine-optimized titles, meta descriptions, slugs, keywords,
content tags, summaries, and accessible image alt text strategies using NVIDIA NIM.
"""

import json
import re
from typing import List, Optional
from pydantic import BaseModel, Field
from app.llm import get_chat_llm
from app.utils.logging import logger
from langchain_core.messages import SystemMessage, HumanMessage


class SEOMetadata(BaseModel):
    """Structured SEO metadata for high-ranking travel blogs."""
    seo_title: str = Field(..., description="Optimized title under 60 characters with main keyword near front")
    meta_description: str = Field(..., description="Compelling description between 140-160 characters with call-to-action")
    slug: str = Field(..., description="Clean, lowercase, hyphenated URL path slug")
    main_keyword: str = Field(..., description="Primary high-intent search query")
    secondary_keywords: List[str] = Field(default_factory=list, description="4-6 latent semantic search terms")
    summary: str = Field(..., description="Crisp 2-3 sentence article teaser summary")
    tags: List[str] = Field(default_factory=list, description="5-8 topical tags for frontend indexing and filtering")
    image_alt_text_suggestions: List[str] = Field(default_factory=list, description="Descriptive alt text for featured and gallery images")


def clean_json_response(raw_text: str) -> str:
    """Strips markdown code fences from LLM responses."""
    text = raw_text.strip()
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        return text[start : end + 1]
    return text


def clean_slug(slug_text: str) -> str:
    """Ensures a slug is lowercase and alphanumeric with hyphens only."""
    text = slug_text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")[:100]


def generate_seo_metadata(
    destination: str,
    country: str,
    category: str,
    article_title: str,
    body_markdown: str,
    unique_angle: str,
) -> SEOMetadata:
    """
    Analyzes generated travel article content to synthesize optimized SEO metadata.
    Avoids keyword stuffing and misleading clickbait.
    """
    # Sample first 1,500 characters of article body for semantic context
    body_sample = body_markdown[:1500].strip()

    system_prompt = (
        "You are the Head of Search Engine Optimization and Audience Growth for GlobeTrotter AI. "
        "Your mission is to craft high-ranking, honest, and compelling SEO metadata for global travel articles.\n\n"
        "STRICT SEO RULES:\n"
        "1. seo_title: 50 to 60 characters maximum. Place the destination and primary keyword near the beginning. "
        "Must be natural, enticing, and accurate without cheesy clickbait.\n"
        "2. meta_description: Exactly 140 to 160 characters. Highlight unique highlights and end with an enticing call-to-action.\n"
        "3. slug: Clean, readable, hyphen-delimited lowercase URL string (3-6 words).\n"
        "4. main_keyword: The single most valuable, high-intent travel search term for this destination.\n"
        "5. secondary_keywords: Exactly 4 latent semantic indexing (LSI) search phrases.\n"
        "6. summary: 2-3 sentences (180-250 characters) summarizing the core experience.\n"
        "7. tags: 5 to 7 relevant categorization tags (e.g. ['Kyoto', 'Japan Travel', 'Zen Temples', 'Heritage', 'Ancient Architecture']).\n"
        "8. image_alt_text_suggestions: 3 highly descriptive, accessible image alt-text phrases for travel photography.\n"
        "9. Avoid keyword stuffing at all costs.\n\n"
        "OUTPUT FORMAT: Return ONLY valid JSON adhering strictly to this schema:\n"
        "{\n"
        '  "seo_title": "Optimized Title (50-60 chars)",\n'
        '  "meta_description": "Compelling meta description with call to action (140-160 chars)",\n'
        '  "slug": "descriptive-readable-url-slug",\n'
        '  "main_keyword": "Primary Search Keyword",\n'
        '  "secondary_keywords": ["keyword 1", "keyword 2", "keyword 3", "keyword 4"],\n'
        '  "summary": "Crisp 2-3 sentence teaser summary",\n'
        '  "tags": ["Tag1", "Tag2", "Tag3", "Tag4", "Tag5"],\n'
        '  "image_alt_text_suggestions": ["Alt text 1", "Alt text 2", "Alt text 3"]\n'
        "}"
    )

    user_prompt = (
        f"Destination: {destination}, {country}\n"
        f"Category: {category}\n"
        f"Article Title: {article_title}\n"
        f"Editorial Angle: {unique_angle}\n\n"
        f"Article Excerpt:\n{body_sample}\n\n"
        "Generate the complete SEO metadata package in JSON now."
    )

    llm = get_chat_llm(temperature=0.3, max_tokens=1500)
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])
        cleaned_json = clean_json_response(response.content)
        parsed = json.loads(cleaned_json)

        # Enforce slug cleanliness
        parsed_slug = clean_slug(parsed.get("slug", article_title))
        parsed["slug"] = parsed_slug

        seo_data = SEOMetadata.model_validate(parsed)
        logger.info(f"[+] Successfully generated SEO metadata for '{destination}': main keyword='{seo_data.main_keyword}'")
        return seo_data

    except Exception as exc:
        logger.warning(f"Error generating SEO metadata: {exc}. Using robust fallback values.")
        fallback_slug = clean_slug(f"{destination}-{category}")
        return SEOMetadata(
            seo_title=f"{destination} Travel Guide: Explore {country}"[:60],
            meta_description=f"Discover the beauty, culture, and attractions of {destination}, {country}. Plan your complete travel itinerary with our essential guide!"[:160],
            slug=fallback_slug,
            main_keyword=f"{destination} travel",
            secondary_keywords=[f"{destination} guide", f"{country} tourism", f"{destination} attractions", f"visit {destination}"],
            summary=f"A complete travel guide exploring the unique cultural and natural wonders of {destination}, {country}.",
            tags=[destination, country, category, "Travel Guide", "Tourism"],
            image_alt_text_suggestions=[
                f"Scenic panoramic view of {destination} in {country}",
                f"Historic architecture and landmark at {destination}",
                f"Local cultural atmosphere and landscape in {destination}"
            ]
        )

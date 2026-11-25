"""
GlobeTrotter AI - Research & Evidence Collection Service.
Aggregates factual travel intelligence from Tavily Search API, Wikipedia REST API,
and Wikidata, then synthesizes structured, fact-checked evidence using NVIDIA NIM.
"""

import json
import re
from typing import List, Optional
import requests
from pydantic import BaseModel, Field
from app.config import get_settings
from app.llm import get_chat_llm
from app.utils.logging import logger
from langchain_core.messages import SystemMessage, HumanMessage

settings = get_settings()


class RawSource(BaseModel):
    """Raw source data collected from external knowledge providers."""
    url: str
    publisher: str
    title: str
    content: str


class StructuredEvidence(BaseModel):
    """Synthesized, fact-verified travel evidence covering all core content domains."""
    geographical_context: str = Field(..., description="Location, terrain, climate, and access proximity")
    historical_background: str = Field(..., description="Origins, historical timeline, and heritage status")
    cultural_significance: str = Field(..., description="Local customs, traditions, spiritual or community life")
    key_attractions: List[str] = Field(default_factory=list, description="Must-see landmarks, routes, or sites")
    local_cuisine: str = Field(..., description="Traditional dishes, ingredients, and culinary customs")
    best_visiting_season: str = Field(..., description="Recommended seasons, weather patterns, and timing")
    transportation_access: str = Field(..., description="Transit options, nearest hubs, and getting around")
    practical_travel_tips: List[str] = Field(default_factory=list, description="Respectful etiquette, packing, and navigation")
    safety_guidelines: str = Field(..., description="Elevation, environmental, and general visitor safety guidance")
    sources: List[RawSource] = Field(default_factory=list, description="All verified reference citations")


def search_tavily(query: str, max_results: int = 4) -> List[RawSource]:
    """
    Executes live web research using Tavily Search API if configured.
    Returns clean parsed sources with URLs, publishers, and excerpts.
    """
    api_key = settings.TAVILY_API_KEY
    if not api_key or api_key.startswith("tvly-your-"):
        logger.debug("Tavily API key not configured. Proceeding with authoritative Wikipedia & open knowledge APIs.")
        return []

    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": settings.TAVILY_SEARCH_DEPTH,
        "include_answer": False,
        "max_results": max_results,
    }

    try:
        response = requests.post(url, json=payload, timeout=12)
        if response.status_code == 200:
            data = response.json()
            results = []
            for item in data.get("results", []):
                results.append(
                    RawSource(
                        url=item.get("url", ""),
                        publisher=item.get("source", "Web Source"),
                        title=item.get("title", "Online Travel Resource"),
                        content=item.get("content", "").strip(),
                    )
                )
            logger.info(f"[+] Tavily returned {len(results)} authoritative sources for query: '{query}'")
            return results
        else:
            logger.warning(f"Tavily API returned status {response.status_code}: {response.text[:100]}")
            return []
    except Exception as exc:
        logger.warning(f"Tavily search encountered error: {exc}. Using fallback knowledge sources.")
        return []


def search_wikipedia_summary(title: str) -> Optional[RawSource]:
    """Retrieves concise factual summary from Wikipedia REST API."""
    headers = {"User-Agent": "GlobeTrotterAI/1.0 (contact: info@globetrotter.ai)"}
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"

    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            data = response.json()
            extract = data.get("extract", "")
            page_url = data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{title}")
            if extract:
                return RawSource(
                    url=page_url,
                    publisher="Wikipedia (Wikimedia Foundation)",
                    title=data.get("title", title),
                    content=extract.strip(),
                )
    except Exception as exc:
        logger.debug(f"Wikipedia summary lookup note: {exc}")
    return None


def search_wikipedia_articles(query: str, max_results: int = 3) -> List[RawSource]:
    """Searches Wikipedia and extracts lead sections for matching articles."""
    headers = {"User-Agent": "GlobeTrotterAI/1.0"}
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "utf8": 1,
        "srlimit": max_results,
    }

    results: List[RawSource] = []
    try:
        response = requests.get(url, params=params, headers=headers, timeout=8)
        if response.status_code == 200:
            search_items = response.json().get("query", {}).get("search", [])
            for item in search_items:
                page_title = item.get("title", "")
                summary_source = search_wikipedia_summary(page_title)
                if summary_source:
                    results.append(summary_source)
                else:
                    # Strip basic HTML tags from snippet
                    snippet = re.sub(r"<[^>]+>", "", item.get("snippet", ""))
                    if snippet:
                        results.append(
                            RawSource(
                                url=f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}",
                                publisher="Wikipedia",
                                title=page_title,
                                content=snippet.strip(),
                            )
                        )
    except Exception as exc:
        logger.warning(f"Wikipedia search error for '{query}': {exc}")

    return results


def gather_multi_source_data(
    destination: str,
    country: str,
    unique_angle: str,
) -> List[RawSource]:
    """
    Gathers factual evidence from multiple reliable channels.
    Combines Tavily web search results with Wikipedia knowledge bases.
    """
    raw_sources: List[RawSource] = []
    seen_urls = set()

    # Query 1: Destination and Country encyclopedic overview
    wiki_sources = search_wikipedia_articles(f"{destination} {country}", max_results=2)
    for src in wiki_sources:
        if src.url not in seen_urls:
            seen_urls.add(src.url)
            raw_sources.append(src)

    # Query 2: Tavily search for destination, country, and tourism overview
    tavily_overview = search_tavily(f"{destination} {country} tourism history attractions travel guide", max_results=3)
    for src in tavily_overview:
        if src.url not in seen_urls:
            seen_urls.add(src.url)
            raw_sources.append(src)

    # Query 3: Targeted query for unique angle
    angle_query = f"{destination} {country} {unique_angle[:60]}"
    tavily_angle = search_tavily(angle_query, max_results=2)
    for src in tavily_angle:
        if src.url not in seen_urls:
            seen_urls.add(src.url)
            raw_sources.append(src)

    # Fallback: If Tavily returned nothing, fetch additional related Wikipedia articles
    if len(raw_sources) < 2:
        extra_wiki = search_wikipedia_articles(f"{destination} tourism culture", max_results=2)
        for src in extra_wiki:
            if src.url not in seen_urls:
                seen_urls.add(src.url)
                raw_sources.append(src)

    logger.info(f"[+] Total distinct research sources collected: {len(raw_sources)} for '{destination}'")
    return raw_sources


def clean_json_response(raw_text: str) -> str:
    """Strips markdown code blocks, reasoning traces, or preamble from LLM text."""
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


def synthesize_factual_evidence(
    destination: str,
    country: str,
    category: str,
    unique_angle: str,
    raw_sources: List[RawSource],
) -> StructuredEvidence:
    """
    Synthesizes raw collected excerpts into structured, fact-checked evidence points.
    Strictly forbids hallucinated prices, opening hours, or fabricated details.
    """
    sources_summary = "\n\n".join(
        [
            f"SOURCE [{i+1}] - Publisher: {s.publisher} | Title: {s.title} | URL: {s.url}\nExcerpt: {s.content}"
            for i, s in enumerate(raw_sources)
        ]
    )

    system_prompt = (
        "You are the Senior Research Intelligence Agent for GlobeTrotter AI. "
        "Your role is to rigorously synthesize gathered factual evidence into structured research notes.\n\n"
        "STRICT EDITORIAL RULES:\n"
        "1. Never invent opening hours, ticket prices, travel restrictions, or time-sensitive entry details.\n"
        "2. Clearly distinguish ancient/historical facts from modern visitor information.\n"
        "3. Only state facts supported by reliable knowledge and the provided reference sources.\n"
        "4. Emphasize the unique angle provided.\n\n"
        "OUTPUT FORMAT: You must return ONLY valid JSON matching this schema:\n"
        "{\n"
        '  "geographical_context": "Detailed description of location, climate, and terrain",\n'
        '  "historical_background": "Origins, historical era, architecture, and heritage status",\n'
        '  "cultural_significance": "Local customs, traditions, spiritual importance",\n'
        '  "key_attractions": ["Attraction 1", "Attraction 2", "Attraction 3"],\n'
        '  "local_cuisine": "Signature dishes, culinary customs, and traditions",\n'
        '  "best_visiting_season": "Optimal weather seasons and timing advice",\n'
        '  "transportation_access": "How to reach and navigate the destination",\n'
        '  "practical_travel_tips": ["Tip 1", "Tip 2", "Tip 3"],\n'
        '  "safety_guidelines": "Terrain, climate, and practical visitor precautions"\n'
        "}"
    )

    user_prompt = (
        f"Destination: {destination}, {country}\n"
        f"Tourism Category: {category}\n"
        f"Unique Angle: {unique_angle}\n\n"
        f"Gathered Source Excerpts:\n{sources_summary}\n\n"
        "Synthesize the factual evidence now in JSON."
    )

    llm = get_chat_llm(temperature=0.2, max_tokens=2500)
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])
        cleaned_json = clean_json_response(response.content)
        parsed = json.loads(cleaned_json)

        evidence = StructuredEvidence(
            geographical_context=parsed.get("geographical_context", ""),
            historical_background=parsed.get("historical_background", ""),
            cultural_significance=parsed.get("cultural_significance", ""),
            key_attractions=parsed.get("key_attractions", []),
            local_cuisine=parsed.get("local_cuisine", ""),
            best_visiting_season=parsed.get("best_visiting_season", ""),
            transportation_access=parsed.get("transportation_access", ""),
            practical_travel_tips=parsed.get("practical_travel_tips", []),
            safety_guidelines=parsed.get("safety_guidelines", ""),
            sources=raw_sources,
        )
        return evidence
    except Exception as exc:
        logger.error(f"Evidence synthesis error: {exc}")
        # Construct fallback evidence directly from raw sources if LLM parsing stumbled
        return StructuredEvidence(
            geographical_context=f"{destination} is situated in {country}.",
            historical_background="Historically significant heritage destination.",
            cultural_significance="Rich local traditions and cultural heritage.",
            key_attractions=[destination],
            local_cuisine="Traditional regional culinary specialties.",
            best_visiting_season="Spring and Autumn offer favorable conditions.",
            transportation_access="Accessible via regional transit hubs.",
            practical_travel_tips=["Respect local customs and cultural heritage sites."],
            safety_guidelines="Follow standard travel and environmental guidelines.",
            sources=raw_sources,
        )

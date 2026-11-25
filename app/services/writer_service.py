"""
GlobeTrotter AI - Article Writer Service.
Generates comprehensive, SEO-friendly, research-backed travel articles in Markdown
following a strict 13-section editorial structure.
"""

import json
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.llm import get_chat_llm
from app.utils.logging import logger
from langchain_core.messages import SystemMessage, HumanMessage


REQUIRED_ARTICLE_SECTIONS = [
    "Introduction",
    "Destination Overview",
    "History and Background",
    "Major Attractions",
    "Culture and Local Experiences",
    "Food and Local Cuisine",
    "Best Time to Visit",
    "Travel Tips",
    "Suggested Itinerary",
    "Important Visitor Information",
    "Conclusion",
    "Sources and References",
]


class SectionOutline(BaseModel):
    section_name: str
    key_points: List[str]


class ArticleOutline(BaseModel):
    title: str
    target_word_count: int = 1500
    sections: List[SectionOutline]


class GeneratedArticleData(BaseModel):
    title: str
    slug: str
    summary: str
    body_markdown: str
    word_count: int
    sections_detected: List[str]


def count_words(text: str) -> int:
    """Accurately counts words in Markdown text, excluding formatting symbols."""
    clean = re.sub(r"[#*_`~>\[\]()!-]", " ", text)
    words = clean.split()
    return len(words)


def slugify_title(title: str) -> str:
    """Converts article title into a clean URL slug."""
    text = title.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")[:120]


def clean_json_response(raw_text: str) -> str:
    """Strips code fences from LLM responses."""
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


def generate_article_outline(
    destination: str,
    country: str,
    category: str,
    proposed_title: str,
    unique_angle: str,
    evidence: Dict[str, Any],
) -> ArticleOutline:
    """
    Stage 1: Generates a detailed 13-section editorial blueprint.
    Ensures that factual evidence collected during research is properly distributed.
    """
    system_prompt = (
        "You are the Executive Managing Editor for GlobeTrotter AI. "
        "Create an in-depth editorial outline for a long-form global travel article (target 1,200–1,800 words).\n"
        "You MUST include the following 12 core sections in this exact order:\n"
        "1. Introduction\n"
        "2. Destination Overview\n"
        "3. History and Background\n"
        "4. Major Attractions\n"
        "5. Culture and Local Experiences\n"
        "6. Food and Local Cuisine\n"
        "7. Best Time to Visit\n"
        "8. Travel Tips\n"
        "9. Suggested Itinerary\n"
        "10. Important Visitor Information\n"
        "11. Conclusion\n"
        "12. Sources and References\n\n"
        "OUTPUT FORMAT: Return ONLY valid JSON adhering to this schema:\n"
        "{\n"
        '  "title": "SEO-friendly Catchy Article Title",\n'
        '  "target_word_count": 1500,\n'
        '  "sections": [\n'
        '    {"section_name": "Section Name", "key_points": ["Point 1", "Point 2", "Point 3"]}\n'
        "  ]\n"
        "}"
    )

    user_prompt = (
        f"Destination: {destination}, {country}\n"
        f"Category: {category}\n"
        f"Proposed Title: {proposed_title}\n"
        f"Unique Angle: {unique_angle}\n\n"
        f"Synthesized Research Evidence:\n"
        f"- Geography: {evidence.get('geographical_context', 'N/A')}\n"
        f"- History: {evidence.get('historical_background', 'N/A')}\n"
        f"- Culture: {evidence.get('cultural_significance', 'N/A')}\n"
        f"- Attractions: {evidence.get('key_attractions', [])}\n"
        f"- Cuisine: {evidence.get('local_cuisine', 'N/A')}\n"
        f"- Timing: {evidence.get('best_visiting_season', 'N/A')}\n"
        f"- Transit: {evidence.get('transportation_access', 'N/A')}\n"
        f"- Tips: {evidence.get('practical_travel_tips', [])}\n\n"
        "Generate the complete outline in JSON."
    )

    llm = get_chat_llm(temperature=0.3, max_tokens=2048)
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])
        cleaned = clean_json_response(response.content)
        parsed = json.loads(cleaned)
        return ArticleOutline.model_validate(parsed)
    except Exception as exc:
        logger.warning(f"Error generating outline with LLM: {exc}. Using standard schema.")
        # Fallback to standard 12-section blueprint
        sections = [
            SectionOutline(section_name=sec, key_points=[f"Explore {sec} for {destination}"])
            for sec in REQUIRED_ARTICLE_SECTIONS
        ]
        return ArticleOutline(title=proposed_title, target_word_count=1500, sections=sections)


def generate_full_article_markdown(
    destination: str,
    country: str,
    category: str,
    unique_angle: str,
    outline: ArticleOutline,
    evidence: Dict[str, Any],
    sources: List[Dict[str, Any]],
) -> GeneratedArticleData:
    """
    Stage 2: Generates the full 1,200–1,800 word Markdown article.
    Enforces natural narrative tone, factual grounding, and formatted references.
    """
    citations_markdown = "\n".join(
        [
            f"- [{s.get('title', 'Reference')}]({s.get('url', '#')}) - *{s.get('publisher', 'Verified Resource')}*"
            for s in sources
        ]
    )

    sections_blueprint = "\n".join(
        [
            f"## {s.section_name}\n" + "\n".join([f"- {p}" for p in s.key_points])
            for s in outline.sections
        ]
    )

    system_prompt = (
        "You are an acclaimed senior travel journalist, cultural historian, and lead writer for GlobeTrotter AI. "
        "Your assignment is to write an exhaustive, evocative, and practical travel article.\n\n"
        "EDITORIAL GUIDELINES:\n"
        "1. Length: Approximately 1,200 to 1,800 words of rich, comprehensive Markdown prose.\n"
        "2. Structure: You MUST follow this exact section structure using Markdown ## headers:\n"
        "   - # [Main Title]\n"
        "   - ## Introduction\n"
        "   - ## Destination Overview\n"
        "   - ## History and Background\n"
        "   - ## Major Attractions\n"
        "   - ## Culture and Local Experiences\n"
        "   - ## Food and Local Cuisine\n"
        "   - ## Best Time to Visit\n"
        "   - ## Travel Tips\n"
        "   - ## Suggested Itinerary\n"
        "   - ## Important Visitor Information\n"
        "   - ## Conclusion\n"
        "   - ## Sources and References\n"
        "3. Writing Style: Warm, sophisticated, immersive, factually anchored. Use sensory descriptions, "
        "sub-headers (###), bullet points for tips/itineraries, and bold typography for key landmarks.\n"
        "4. Factuality: Strictly rely on the provided evidence. Do NOT invent opening hours, prices, or false dates.\n"
        "5. Unique Angle: Deeply integrate the requested unique editorial angle throughout the narrative.\n"
        "6. In the final '## Sources and References' section, format the provided citations as Markdown links."
    )

    user_prompt = (
        f"Destination: {destination}, {country}\n"
        f"Category: {category}\n"
        f"Title: {outline.title}\n"
        f"Unique Angle: {unique_angle}\n\n"
        f"Research Evidence:\n"
        f"- Geographical Context: {evidence.get('geographical_context')}\n"
        f"- Historical Background: {evidence.get('historical_background')}\n"
        f"- Cultural Significance: {evidence.get('cultural_significance')}\n"
        f"- Key Attractions: {', '.join(evidence.get('key_attractions', []))}\n"
        f"- Local Cuisine: {evidence.get('local_cuisine')}\n"
        f"- Best Visiting Season: {evidence.get('best_visiting_season')}\n"
        f"- Transportation Access: {evidence.get('transportation_access')}\n"
        f"- Practical Travel Tips: {evidence.get('practical_travel_tips')}\n"
        f"- Safety Guidelines: {evidence.get('safety_guidelines')}\n\n"
        f"Reference Citations to Include in Bibliography:\n{citations_markdown}\n\n"
        f"Outline Blueprint:\n{sections_blueprint}\n\n"
        "Write the complete, long-form travel article in Markdown now."
    )

    llm = get_chat_llm(temperature=0.7, max_tokens=4096)
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])
    article_markdown = response.content.strip()

    # Ensure Sources section is present
    if "## Sources and References" not in article_markdown and citations_markdown:
        article_markdown += f"\n\n## Sources and References\n{citations_markdown}"

    # Extract detected sections
    headers = re.findall(r"^##\s+(.+)$", article_markdown, flags=re.MULTILINE)

    # Generate summary from first paragraphs
    paragraphs = [p.strip() for p in article_markdown.split("\n\n") if p.strip() and not p.strip().startswith("#")]
    summary = paragraphs[0] if paragraphs else f"A comprehensive guide to discovering {destination}, {country}."
    if len(summary) > 400:
        summary = summary[:397] + "..."

    word_count = count_words(article_markdown)
    slug = slugify_title(outline.title)

    logger.info(f"[+] Generated article '{outline.title}': {word_count} words, {len(headers)} sections detected.")

    return GeneratedArticleData(
        title=outline.title,
        slug=slug,
        summary=summary,
        body_markdown=article_markdown,
        word_count=word_count,
        sections_detected=headers,
    )

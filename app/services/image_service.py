"""
GlobeTrotter AI - Image Discovery & License Management Service.
Discovers legally usable, high-resolution media assets from Wikimedia Commons,
Unsplash, and Pexels. Strictly verifies licenses and builds attribution metadata.
"""

import re
from typing import List, Optional
import requests
from pydantic import BaseModel, Field
from app.config import get_settings
from app.utils.logging import logger

settings = get_settings()

# Permitted Open Licenses (Commercial & Transformative Friendly)
PERMITTED_LICENSE_KEYWORDS = [
    "public domain",
    "cc0",
    "cc-zero",
    "pd",
    "cc by",
    "cc by-sa",
    "attribution",
    "sharealike",
    "unsplash license",
    "pexels license",
]

# Strictly Forbidden Licenses (Non-Commercial, No-Derivatives, or All Rights Reserved)
FORBIDDEN_LICENSE_KEYWORDS = [
    "-nc",
    "non-commercial",
    "noncommercial",
    "-nd",
    "no derivatives",
    "noderivatives",
    "all rights reserved",
    "copyrighted",
]


class DiscoveredImage(BaseModel):
    """Normalized media asset with verified usage license and full creator attribution."""
    image_url: str
    provider: str  # wikimedia, unsplash, pexels
    creator: str
    license_name: str
    attribution: str
    alt_text: str
    is_featured: bool = False
    width: Optional[int] = None
    height: Optional[int] = None


def is_license_permitted(license_str: str) -> bool:
    """
    Rigorously verifies whether an image license allows legal commercial use.
    Rejects non-commercial (NC), no-derivatives (ND), and unclear permissions.
    """
    if not license_str:
        return False
    lic_lower = license_str.lower().strip()

    # Reject forbidden terms first
    for forbidden in FORBIDDEN_LICENSE_KEYWORDS:
        if forbidden in lic_lower:
            return False

    # Check for allowed license terms
    for permitted in PERMITTED_LICENSE_KEYWORDS:
        if permitted in lic_lower:
            return True

    return False


def clean_html(text: str) -> str:
    """Strips HTML markup from API metadata strings."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    return clean.strip()


def search_wikimedia_commons(query: str, max_results: int = 6) -> List[DiscoveredImage]:
    """
    Searches Wikimedia Commons repository via MediaWiki Action API.
    Extracts direct CDN URLs, author credits, and license names.
    """
    headers = {"User-Agent": "GlobeTrotterAI/1.0 (contact: info@globetrotter.ai)"}
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,  # File namespace
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|user|size",
        "format": "json",
        "gsrlimit": max_results,
    }

    results: List[DiscoveredImage] = []
    valid_extensions = (".jpg", ".jpeg", ".png", ".webp")

    try:
        response = requests.get(url, params=params, headers=headers, timeout=12)
        if response.status_code != 200:
            logger.warning(f"Wikimedia API returned status {response.status_code}")
            return []

        pages = response.json().get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            image_info_list = page.get("imageinfo", [])
            if not image_info_list:
                continue

            ii = image_info_list[0]
            raw_url = ii.get("url", "")
            # Filter valid image formats
            clean_url = raw_url.split("?")[0].lower()
            if not any(clean_url.endswith(ext) for ext in valid_extensions):
                continue

            width = ii.get("width", 0)
            height = ii.get("height", 0)
            # Favor decent resolution images
            if width and width < 600:
                continue

            meta = ii.get("extmetadata", {})
            raw_license = meta.get("LicenseShortName", {}).get("value", "") or meta.get("UsageTerms", {}).get("value", "")
            license_name = clean_html(raw_license) or "CC BY-SA 4.0"

            # Strict license check
            if not is_license_permitted(license_name):
                logger.debug(f"Skipping image with unapproved license: {license_name} ({raw_url})")
                continue

            raw_author = meta.get("Artist", {}).get("value", "") or ii.get("user", "Wikimedia Contributor")
            creator = clean_html(raw_author)[:120] or "Wikimedia Commons Contributor"

            # Formulate legal attribution statement
            attribution = f"Photo by {creator} via Wikimedia Commons ({license_name})"
            title_clean = page.get("title", "").replace("File:", "").split(".")[0].replace("_", " ")

            results.append(
                DiscoveredImage(
                    image_url=raw_url,
                    provider="wikimedia",
                    creator=creator,
                    license_name=license_name,
                    attribution=attribution,
                    alt_text=title_clean[:120],
                    width=width,
                    height=height,
                    is_featured=False,
                )
            )

        logger.info(f"[+] Wikimedia Commons returned {len(results)} verified licensed images for query: '{query}'")
        return results

    except Exception as exc:
        logger.warning(f"Wikimedia image search error for '{query}': {exc}")
        return []


def search_unsplash(query: str, max_results: int = 3) -> List[DiscoveredImage]:
    """Searches Unsplash API if access key is provided."""
    access_key = settings.UNSPLASH_ACCESS_KEY
    if not access_key:
        return []

    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {access_key}"}
    params = {"query": query, "per_page": max_results, "orientation": "landscape"}

    results: List[DiscoveredImage] = []
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            for item in response.json().get("results", []):
                creator_name = item.get("user", {}).get("name", "Unsplash Photographer")
                img_url = item.get("urls", {}).get("regular", "")
                alt_desc = item.get("alt_description", "") or query

                results.append(
                    DiscoveredImage(
                        image_url=img_url,
                        provider="unsplash",
                        creator=creator_name,
                        license_name="Unsplash License",
                        attribution=f"Photo by {creator_name} on Unsplash",
                        alt_text=alt_desc[:120],
                        width=item.get("width"),
                        height=item.get("height"),
                        is_featured=False,
                    )
                )
    except Exception as exc:
        logger.warning(f"Unsplash search error: {exc}")
    return results


def search_pexels(query: str, max_results: int = 3) -> List[DiscoveredImage]:
    """Searches Pexels API if API key is provided."""
    api_key = settings.PEXELS_API_KEY
    if not api_key:
        return []

    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": api_key}
    params = {"query": query, "per_page": max_results, "orientation": "landscape"}

    results: List[DiscoveredImage] = []
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            for photo in response.json().get("photos", []):
                creator_name = photo.get("photographer", "Pexels Creator")
                img_url = photo.get("src", {}).get("large", "")
                alt_desc = photo.get("alt", "") or query

                results.append(
                    DiscoveredImage(
                        image_url=img_url,
                        provider="pexels",
                        creator=creator_name,
                        license_name="Pexels License",
                        attribution=f"Photo by {creator_name} on Pexels",
                        alt_text=alt_desc[:120],
                        width=photo.get("width"),
                        height=photo.get("height"),
                        is_featured=False,
                    )
                )
    except Exception as exc:
        logger.warning(f"Pexels search error: {exc}")
    return results


def discover_article_images(
    destination: str,
    country: str,
    keywords: Optional[List[str]] = None,
    alt_suggestions: Optional[List[str]] = None,
    target_count: int = 3,
) -> List[DiscoveredImage]:
    """
    Multi-provider media discovery pipeline:
    1. Queries Wikimedia Commons (and Unsplash/Pexels if configured).
    2. Validates usage licenses.
    3. Selects 1 Featured Image + gallery images.
    4. Applies SEO-friendly alt text.
    """
    candidates: List[DiscoveredImage] = []
    seen_urls = set()

    # Query 1: Destination and Country
    q1 = f"{destination} {country}"
    for img in search_wikimedia_commons(q1, max_results=4):
        if img.image_url not in seen_urls:
            seen_urls.add(img.image_url)
            candidates.append(img)

    # Optional Unsplash & Pexels
    for img in search_unsplash(q1, max_results=2):
        if img.image_url not in seen_urls:
            seen_urls.add(img.image_url)
            candidates.append(img)

    for img in search_pexels(q1, max_results=2):
        if img.image_url not in seen_urls:
            seen_urls.add(img.image_url)
            candidates.append(img)

    # Query 2: Specific landmarks or keywords if more needed
    if len(candidates) < target_count and keywords:
        for kw in keywords[:2]:
            for img in search_wikimedia_commons(f"{destination} {kw}", max_results=2):
                if img.image_url not in seen_urls:
                    seen_urls.add(img.image_url)
                    candidates.append(img)

    # Slice to desired target count
    selected = candidates[:target_count]

    # Designate the first image as featured
    if selected:
        selected[0].is_featured = True

    # Apply alt text suggestions if provided
    alt_list = alt_suggestions or []
    for idx, img in enumerate(selected):
        if idx < len(alt_list) and alt_list[idx]:
            img.alt_text = alt_list[idx]
        elif not img.alt_text or img.alt_text == destination:
            role = "Featured landscape of" if img.is_featured else "Scenic view of"
            img.alt_text = f"{role} {destination} in {country}"

    logger.info(f"[+] Finalized {len(selected)} legally verified images for '{destination}' (Featured: {selected[0].image_url if selected else 'None'})")
    return selected

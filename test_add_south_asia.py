"""
Generate and publish a South & Central Asia article with Waterfalls, Mountains & Natural Wonders.
"""

from app.database.session import SessionLocal
from app.database.models import Topic, Article
from app.graph.workflow import run_globetrotter_pipeline
from app.services.publisher_service import publish_article
from app.graph.nodes.duplicate_check import generate_canonical_key


def generate_south_asia_mountain_story():
    db = SessionLocal()
    destination = "Annapurna Sanctuary"
    country = "Nepal"
    region = "South & Central Asia"
    category = "Waterfalls, Mountains & Natural Wonders"
    proposed_title = "Annapurna Sanctuary: Glacial Amphitheaters and Sacred Himalayan Peaks"
    unique_angle = "Trekking through rhododendron cloud forests into the high-altitude glacial amphitheater beneath Annapurna and Machapuchare."

    canonical_key = generate_canonical_key(destination, category, unique_angle)

    existing_topic = db.query(Topic).filter(Topic.canonical_key == canonical_key).first()
    if not existing_topic:
        existing_topic = Topic(
            canonical_key=canonical_key,
            destination=destination,
            country=country,
            category=category,
            proposed_title=proposed_title,
            unique_angle=unique_angle,
            discovery_source="editorial_curation",
            status="discovered",
        )
        db.add(existing_topic)
        db.commit()
        db.refresh(existing_topic)

    topic_id = existing_topic.id
    db.close()

    print(f"[*] Invoking LangGraph for {destination} (Topic ID {topic_id})...")
    state_input = {
        "topic_id": topic_id,
        "destination": destination,
        "country": country,
        "category": category,
        "region": region,
        "proposed_title": proposed_title,
        "unique_angle": unique_angle,
    }

    final_state = run_globetrotter_pipeline(state_input)
    article_id = final_state.get("article_id")
    print(f"[+] LangGraph generated Article ID: {article_id}")

    if article_id:
        db = SessionLocal()
        job, payload = publish_article(db, article_id)
        db.close()
        print(f"[+] Successfully published Article {article_id} to '{payload['website_url']}'")


if __name__ == "__main__":
    generate_south_asia_mountain_story()

# GlobeTrotter AI — LangGraph Orchestration Architecture

This architecture document presents the complete visual flow and state transition graph of the autonomous multi-agent pipeline powering GlobeTrotter AI.

---

## 1. Compiled LangGraph Visual Graph

The rendered graph diagram generated directly from the compiled LangGraph state machine:

![GlobeTrotter AI LangGraph Workflow](/C:/Users/Administrator/.gemini/antigravity/brain/f294baf5-ea0d-46a7-b346-e65b1a408c51/workflow_graph.png)

*Direct local image link: [workflow_graph.png](file:///c:/Users/Administrator/Downloads/project_tourist/workflow_graph.png)*

---

## 2. Interactive Mermaid Flowchart

```mermaid
flowchart TD
    classDef startEnd fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef process fill:#1e293b,stroke:#0d9488,stroke-width:2px,color:#f8fafc;
    classDef decision fill:#312e81,stroke:#818cf8,stroke-width:2px,color:#f8fafc;
    classDef loop fill:#451a03,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;

    START([Start Pipeline]):::startEnd --> discover_node["Node 1: Topic Discovery<br/>(Worldwide 10-Region Balanced Rotation)"]:::process
    discover_node --> deduplicate_node{"Node 2: Deduplication Gate<br/>(L1 Canonical & L2 Semantic Check)"}:::decision
    
    deduplicate_node -->|"Duplicate Found"| END_DUP([End: Reject Duplicate & Trigger Next Angle]):::startEnd
    deduplicate_node -->|"Novel Angle"| research_node["Node 3: Research & Citations<br/>(Tavily / Wikipedia / Wikidata Rest APIs)"]:::process
    
    research_node --> writer_node["Node 4: Editorial Writer<br/>(12-Section Long-Form Narrative)"]:::process
    writer_node --> seo_node["Node 5: SEO Optimization<br/>(Slug, Meta Description, Search Keywords)"]:::process
    seo_node --> image_node["Node 6: Permitted Media Search<br/>(Wikimedia Commons Discovery & Attribution)"]:::process
    image_node --> quality_node{"Node 7: 11-Dimension Quality Gate<br/>(Evaluates Score &ge; 8.0/10)"}:::decision
    
    quality_node -->|"Passed (Score &ge; 8.0)"| END_PASSED([End: Quality Passed & Auto-Published]):::startEnd
    quality_node -->|"Revisions Exhausted"| END_REVIEW([End: Marked for Admin Review]):::startEnd
    quality_node -->|"Below Threshold"| revision_node["Node 8: Targeted Revisions<br/>(Corrective Polish & Section Repair)"]:::loop
    
    revision_node --> quality_node
```

---

## 3. Node Responsibility Breakdown

| Node Name | Module Reference | Primary Responsibility |
| :--- | :--- | :--- |
| **`discover_node`** | `app/graph/nodes/discovery.py` | Rotates through 10 global regions and 13 tourism genres to find balanced, unexplored destinations. |
| **`deduplicate_node`** | `app/graph/nodes/duplicate_check.py` | Computes canonical SHA-256 keys and checks existing topics in PostgreSQL to eliminate duplicate coverage. |
| **`research_node`** | `app/graph/nodes/research.py` | Gathers real-time historical facts, cultural insights, practical logistics, and verifiable citations. |
| **`writer_node`** | `app/graph/nodes/writer.py` | Generates engaging, long-form travel narratives across 12 structured editorial sections. |
| **`seo_node`** | `app/graph/nodes/seo.py` | Produces search-engine-optimized slugs, meta summaries, and taxonomy tags. |
| **`image_node`** | `app/graph/nodes/image_search.py` | Discovers verified, freely licensed imagery with full attribution metadata. |
| **`quality_node`** | `app/services/evaluator_service.py` | Scores the article across 11 criteria (factual depth, structure, tone, voice). Only scores $\ge 8.0$ pass automatically. |
| **`revision_node`** | `app/services/evaluator_service.py` | Performs targeted corrective rewrites if an article scores below the 8.0 threshold before re-evaluation. |

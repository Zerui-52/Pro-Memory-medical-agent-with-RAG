import requests
import re
from typing import List, Dict, Tuple


_HEADERS = {"User-Agent": "MedicalAgent/1.0 (research project; contact@example.com)"}


def hybrid_search(query: str) -> Tuple[List[Dict], float]:
    try:
        resp = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": f"{query} medical",
                "format": "json",
                "srlimit": 5,
                "srprop": "snippet",
            },
            headers=_HEADERS,
            timeout=10,
        ).json()
    except Exception:
        try:
            resp = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "format": "json",
                    "srlimit": 3,
                },
                headers=_HEADERS,
                timeout=10,
            ).json()
        except Exception:
            return [], 0.0

    results = resp.get("query", {}).get("search", [])
    docs = []
    all_keywords = set()

    for r in results:
        snippet = re.sub(r"<[^>]+>", "", r.get("snippet", ""))
        title = r.get("title", "")
        text = f"{title}: {snippet}"
        keywords = set(re.findall(r"\w+", title.lower()))
        all_keywords.update(keywords)
        docs.append({
            "text": text[:500],
            "source": f"wikipedia_{title}",
            "keywords": list(keywords),
            "semantic_score": 0.7 if docs else 0.6,
        })

    query_tokens = set(re.findall(r"\w+", query.lower()))
    coverage = len(query_tokens & all_keywords) / max(len(query_tokens), 1) if query_tokens else 0.0

    return docs[:5], coverage

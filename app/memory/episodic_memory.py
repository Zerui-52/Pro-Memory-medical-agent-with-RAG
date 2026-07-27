from app.retrieval.tag_filter import tag_filter
from app.retrieval.vector_search import vector_search
from app.retrieval.rerank import rerank


def retrieve_episodic(state):
    query = state.get("retrieval_query") or state["merged_question"]

    clusters = tag_filter(query)
    candidates = []
    for c in clusters:
        candidates += vector_search(query, cluster=c, top_k=5)

    ranked = rerank(query, candidates)
    return ranked[:state.get("episodic_k", 8)]
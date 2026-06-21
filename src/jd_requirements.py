"""
This file just writes down, in a structured way, what the Senior AI
Engineer job actually wants. We'll use this later to score candidates.
"""

# Skills that genuinely matter for this role.
# Each group has a few different ways people might write the same skill.
CORE_SKILLS = {
    "embeddings": ["sentence-transformers", "bge", "e5", "embedding"],
    "vector_search": ["pinecone", "weaviate", "qdrant", "milvus",
                       "elasticsearch", "faiss", "vector database"],
    "ranking_eval": ["ndcg", "mrr", "learning to rank", "a/b test"],
    "python": ["python"],
}

# Companies the JD said it does NOT want a career built entirely around
SERVICES_ONLY_COMPANIES = {
    "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini",
    "mindtree", "hcl", "tech mahindra", "ltimindtree", "mphasis",
}

# Locations Redrob prefers
PREFERRED_LOCATIONS = {"pune", "noida"}

# The JD wants roughly 5-9 years of experience (flexible)
EXPERIENCE_RANGE = (5, 9)
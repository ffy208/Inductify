"""
Extract policy chunks from eval_vectordb into a policy-only ChromaDB.
No API calls needed — reuses stored embeddings.
"""
import chromadb
import shutil

SRC = "data/eval_vectordb"
DST = "data/policy_vectordb"

shutil.rmtree(DST, ignore_errors=True)

src = chromadb.PersistentClient(path=SRC)
src_coll = src.get_collection("langchain")

results = src_coll.get(include=["embeddings", "documents", "metadatas"], limit=10000)

policy_ids, policy_embs, policy_docs, policy_meta = [], [], [], []
for i, meta in enumerate(results["metadatas"]):
    if meta.get("source", "").startswith("p_"):
        policy_ids.append(results["ids"][i])
        policy_embs.append(results["embeddings"][i])
        policy_docs.append(results["documents"][i])
        policy_meta.append(meta)

print(f"Policy chunks extracted: {len(policy_ids)}")

dst = chromadb.PersistentClient(path=DST)
dst_coll = dst.create_collection("langchain")

# Add in batches to avoid memory issues
BATCH = 500
for start in range(0, len(policy_ids), BATCH):
    end = start + BATCH
    dst_coll.add(
        ids=policy_ids[start:end],
        embeddings=policy_embs[start:end],
        documents=policy_docs[start:end],
        metadatas=policy_meta[start:end],
    )
    print(f"  Added {min(end, len(policy_ids))}/{len(policy_ids)}")

print(f"Done: {DST} has {dst_coll.count()} chunks")

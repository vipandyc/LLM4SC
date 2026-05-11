import dimcli
import pandas as pd
import time
import math

# --- load the 120k paper IDs ---
df = pd.read_csv("superconduct_top10percent.csv", usecols=["id"])
paper_ids = df["id"].dropna().unique().tolist()
print(f"{len(paper_ids)} ids loaded")

# --- login to Dimensions ---
with open("my_dim_key.txt") as f:
    API_KEY = f.read().strip()

dimcli.login(key=API_KEY)
dsl = dimcli.Dsl()

# --- fetch references for a batch of up to 400 papers ---
def fetch_refs(batch):
    id_list = ", ".join(f'"{pid}"' for pid in batch)
    q = f"""
    search publications
    where id in [{id_list}]
    return publications[id + reference_ids]
    """
    return dsl.query_iterative(q, limit=400, pause=0.5).as_dataframe()


# --- loop over all paper IDs in batches ---
edges = []
batch_size = 400
total_batches = math.ceil(len(paper_ids) / batch_size)

for i in range(total_batches):
    chunk = paper_ids[i * batch_size : (i + 1) * batch_size]
    print(f"batch {i+1}/{total_batches} …")
    df_chunk = fetch_refs(chunk)

    if not df_chunk.empty:
        df_chunk = df_chunk.explode("reference_ids").dropna()
        edges.extend(zip(df_chunk["id"], df_chunk["reference_ids"]))

    time.sleep(1.0)  # be kind to the API

# --- save the citation edge list ---
edges_df = pd.DataFrame(edges, columns=["source", "target"])
edges_df.to_csv("citation_edges_outgoing.csv", index=False)
print(f"saved {len(edges_df)} edges → citation_edges_outgoing.csv")

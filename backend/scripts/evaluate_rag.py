
import json
import requests
import statistics
import time
import sys
import os
from typing import List, Dict, Any
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.core.security import create_access_token
from app.core.config import settings
from datetime import timedelta

# Configuration
API_URL = "http://localhost:8000/api/v1/retrieval/search"
DATASET_PATH = Path(__file__).parent.parent / "tests" / "data" / "rag_gold_dataset.json"
TOP_K = 10

def get_admin_token():
    # Generate token for user_id=1 (assuming Admin)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject="1", expires_delta=access_token_expires
    )
    return token

class RAGEvaluator:
    def __init__(self, api_url: str, dataset_path: Path):
        self.api_url = api_url
        self.dataset = self._load_dataset(dataset_path)
        self.token = get_admin_token()
        self.results = []

    def _load_dataset(self, path: Path) -> List[Dict]:
        if not path.exists():
            print(f"Error: Dataset not found at {path}")
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def run_evaluation(self):
        print(f"Starting evaluation on {len(self.dataset)} queries...")
        print(f"Target API: {self.api_url}")
        
        for item in self.dataset:
            query = item["query"]
            expected_section = item.get("expected_section", "")
            expected_doc = item.get("expected_doc", "")
            
            # Call API
            start_time = time.time()
            try:
                response = requests.post(
                    self.api_url, 
                    json={"query": query, "top_k": TOP_K},
                    timeout=30,
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                response.raise_for_status()
                retrieved_docs = response.json()
            except Exception as e:
                print(f"Failed query '{query}': {e}")
                self.results.append({
                    "query": query,
                    "success": False,
                    "error": str(e)
                })
                continue
            
            latency = time.time() - start_time
            
            # Metric Calculation: Fuzzy Match against Expected Section
            # We check if 'expected_section' (e.g. "1.1 Purpose") appears in 
            # the Retrieved Text OR Metadata.
            # This is a proxy for "Did we retrieve the right chunk?".
            
            first_relevant_rank = None
            hits_at_k = {k: 0 for k in [3, 5, 10]}
            
            retrieved_simples = []

            for i, doc in enumerate(retrieved_docs):
                current_rank = i + 1
                text = doc.get("text", "")
                meta = doc.get("metadata", {})
                
                # Create a searchable blob
                content_blob = (text + " " + str(meta)).lower()
                
                # Check match (simple robust logic: does the section ID appear?)
                # Extract specific marker from expected section like "1.1" or "3.2"
                # OR check full string
                is_match = False
                
                # Heuristic 1: If expected section identifier (e.g. "1.1") is in content
                # This assumes section numbers are unique and preserved.
                section_id = expected_section.split(" ")[0] if " " in expected_section else expected_section
                section_title = expected_section.lower()
                
                if section_id.lower() in content_blob or section_title in content_blob:
                     is_match = True
                
                retrieved_simples.append({
                    "rank": current_rank,
                    "text_snippet": text[:50] + "...",
                    "is_match": is_match
                })

                if is_match:
                    if first_relevant_rank is None:
                        first_relevant_rank = current_rank
                    
                    if current_rank <= 3: hits_at_k[3] = 1
                    if current_rank <= 5: hits_at_k[5] = 1
                    if current_rank <= 10: hits_at_k[10] = 1

            self.results.append({
                "query": query,
                "success": True,
                "latency": latency,
                "hits_at_k": hits_at_k,
                "mrr": 1.0 / first_relevant_rank if first_relevant_rank else 0.0,
                "expected_section": expected_section,
                "retrieved_summary": retrieved_simples
            })

    def print_report(self):
        if not self.results:
            print("No results to report.")
            return

        total = len(self.results)
        successful = sum(1 for r in self.results if r.get("success"))
        
        if successful == 0:
            print("All queries failed.")
            return

        recall_3 = sum(r["hits_at_k"][3] for r in self.results if r.get("success")) / successful
        recall_5 = sum(r["hits_at_k"][5] for r in self.results if r.get("success")) / successful
        recall_10 = sum(r["hits_at_k"][10] for r in self.results if r.get("success")) / successful
        mrr = statistics.mean(r["mrr"] for r in self.results if r.get("success"))
        avg_latency = statistics.mean(r["latency"] for r in self.results if r.get("success"))

        print("\n" + "="*40)
        print("RAG EVALUATION REPORT (Fuzzy Section Match)")
        print("="*40)
        print(f"Total Queries: {total}")
        print(f"Successful:    {successful}")
        print("-" * 20)
        print(f"Recal@3:       {recall_3:.2%}")
        print(f"Recall@5:      {recall_5:.2%}")
        print(f"Recall@10:     {recall_10:.2%}")
        print(f"MRR:           {mrr:.4f}")
        print(f"Avg Latency:   {avg_latency:.4f}s")
        print("="*40)
        
        # Failure Analysis (Zero Recall@5)
        print("\nTop Failures (Recall@5 = 0):")
        failures = [r for r in self.results if r.get("success") and r["hits_at_k"][5] == 0]
        for f in failures[:5]:
            print(f"- Query: {f['query']}")
            print(f"  Expected: {f['expected_section']}")
            print(f"  Top Retrieved: {[r['text_snippet'] for r in f['retrieved_summary'][:3]]}")
            print("-" * 20)

if __name__ == "__main__":
    if not DATASET_PATH.exists():
        # Create dummy if not exists for first run
        print("Dataset not found. Creating dummy dataset...")
        DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DATASET_PATH, "w") as f:
            json.dump([{
                "query": "test query",
                "expected_ids": ["dummy_id"],
                "notes": "Auto-generated dummy"
            }], f)
            
    evaluator = RAGEvaluator(API_URL, DATASET_PATH)
    evaluator.run_evaluation()
    evaluator.print_report()

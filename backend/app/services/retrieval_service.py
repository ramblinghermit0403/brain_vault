from typing import List, Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from sqlalchemy.orm import selectinload
from app.models.document import Chunk
from app.services.vector_store import vector_store

class RetrievalService:
    async def search_memories(
        self, 
        query: str, 
        user_id: int, 
        db: AsyncSession, 
        top_k: int = 5,
        view: str = "auto"
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant artifacts using the specified View.
        Views:
        - semantic: Vector Search (Default)
        - state: Fact Store Lookup (Current Truth)
        - episodic: Time-based Memory Log
        - auto: Hybrid (Logic to select best view, currently defaults to semantic+state)
        """
        if view == "state":
            return await self._search_state(query, user_id, db, top_k)
        elif view == "episodic":
            return await self._search_episodic(query, user_id, db, top_k)
        elif view == "semantic":
            return await self._search_semantic(query, user_id, db, top_k)
        else:
            # Auto: Unified Search (Single Vector Call)
            str_user_id = str(user_id)
            
            # Fetch candidates for both Facts and Memories in one go
            unified_results = await self._search_unified(query, str_user_id, top_k=top_k)
            
            import asyncio
            # Pass pre-fetched candidates to ranking methods
            # _search_state needs int user_id for SQL, _search_semantic needs int or str?
            # Let's look at signatures. _search_state(user_id: int). _search_semantic(user_id: int).
            # So pass user_id (int) to both.
            # state_task = self._search_state(query, user_id, db, top_k=3, pre_fetched=unified_results["facts"])
            # semantic_task = self._search_semantic(query, user_id, db, top_k=top_k, pre_fetched=unified_results["memories"])
            
            # fix: AsyncSession cannot be shared across concurrent tasks. Run sequentially.
            state_results = await self._search_state(query, user_id, db, top_k=3, pre_fetched=unified_results["facts"])
            semantic_results = await self._search_semantic(query, user_id, db, top_k=top_k, pre_fetched=unified_results["memories"])
            
            # results = await asyncio.gather(state_task, semantic_task)
            # state_results, semantic_results = results
            
            return state_results + semantic_results

    async def _search_unified(self, query: str, user_id: str, top_k: int) -> Dict[str, Any]:
        """
        Single Vector Search for both Facts and Memories.
        Returns: {"facts": vector_results, "memories": vector_results}
        """
        # Fetch 10x to allow for MMR and filtering
        fetch_k = top_k * 10
        
        results = await vector_store.query(
            query,
            n_results=fetch_k,
            where={
                "user_id": user_id,
                # Filter for chunks (memories) OR facts
                # "type": {"$in": ["fact", "memory", "chunk"]} # Pinecone metadatas are flat, logic depends on store wrapper
                # Assuming vector_store handles filtering or we filter post-fetch if store is limited
            },
            include_values=True 
        )
        
        # Split results by type
        facts_res = {"ids": [[]], "distances": [[]], "metadatas": [[]], "embeddings": [[]], "documents": [[]]}
        mems_res = {"ids": [[]], "distances": [[]], "metadatas": [[]], "embeddings": [[]], "documents": [[]]}
        
        if results and results.get("ids") and results["ids"][0]:
            for i, metadata in enumerate(results["metadatas"][0]):
                type_val = metadata.get("type", "memory")
                
                # Helper to append to the correct dict structure
                target = facts_res if type_val == "fact" else mems_res
                
                target["ids"][0].append(results["ids"][0][i])
                if results["distances"]: target["distances"][0].append(results["distances"][0][i])
                if results["embeddings"]: target["embeddings"][0].append(results["embeddings"][0][i])
                if results["documents"]: target["documents"][0].append(results["documents"][0][i])
                target["metadatas"][0].append(metadata)
                
        return {"facts": facts_res, "memories": mems_res}

    async def _search_state(self, query: str, user_id: int, db: AsyncSession, top_k: int = 5, pre_fetched: Dict = None) -> List[Dict[str, Any]]:
        """
        Search for current truths (Facts) using Hybrid Strategy:
        1. Semantic Search (Vector Store) -> Finds "parade" from "procession"
        2. Keyword Search (SQL) -> Finds exact matches
        3. Merge & Rank (Semantic + Recency)
        """
        from app.models.fact import Fact
        from sqlalchemy import or_
        import re

        semantic_fact_ids = []
        fact_score_map = {} # Map ID -> Vector Distance/Score

        try:
             # 1. Semantic Search (Vector Store) - Primary Matcher
             if pre_fetched:
                 vector_results = pre_fetched
             else:
                 # Fetch more candidates to allow for filtering
                 vector_results = await vector_store.query(
                     query_texts=query, 
                     n_results=top_k * 4, 
                     where={"user_id": str(user_id), "type": "fact"} 
                 )
             
             if vector_results and vector_results.get("ids"):
                 for i, rid in enumerate(vector_results["ids"][0]):
                     # rid format: "fact_123"
                     if rid.startswith("fact_"):
                         try:
                             fid = int(rid.split("_")[1])
                             semantic_fact_ids.append(fid)
                             # Store distance/score if needed for ranking
                             # pinecone returns similarity (higher = better? or distance?)
                             # Assuming score from vector_store wrapper is useful
                             dist = vector_results["distances"][0][i] if vector_results.get("distances") else 0
                             fact_score_map[fid] = dist
                         except:
                             pass
        except Exception as e:
             # Soft fail if vector search unavailable
             print(f"Vector search for facts failed: {e}")
             return []

        if not semantic_fact_ids:
            return []

        # 2. SQL Hydration (Get actual Fact objects)
        # We ONLY fetch what Vector Store found. No fuzzy keyword search.
        filters = [
            Fact.user_id == user_id, 
            Fact.valid_until == None,
            Fact.is_superseded == False,
            Fact.id.in_(semantic_fact_ids)
        ]
        
        # Fetch Facts with Eager Loading of Chunk for context
        stmt = select(Fact).options(selectinload(Fact.chunk)).where(*filters)
        result = await db.execute(stmt)
        facts = result.scalars().all()
        
        # 3. Ranking
        ranked_facts = []
        for f in facts:
            score = f.confidence or 1.0
            
            # Vector Score Boost
            # Use the score from Vector Store if available, or rank index
            if f.id in fact_score_map:
                # Map vector score directly? 
                # Or use rank-based boost as before (more stable)
                rank_idx = semantic_fact_ids.index(f.id)
                score += 2.0 - (rank_idx * 0.1)
                
                # Optional: Add raw vector score?
                # score += fact_score_map[f.id] * 0.5 
 
            
            # Recency Boost (User Request: "recent one should be given more score")
            # Logic: Add up to +0.5 score for facts within last 30 days.
            # Decay: +0.1 for facts within last year.
            # Formula: 1 / (1 + log(days + 1))? 
            # Simple Linear Bonus:
            if f.valid_from:
                # Ensure timezone awareness (valid_from is usually tz-aware in model, but verify)
                vf = f.valid_from
                if vf.tzinfo is None:
                    vf = vf.replace(tzinfo=timezone.utc)
                
                # Compare to Now (UTC)
                now = datetime.now(timezone.utc)
                age_delta = now - vf
                days_old = max(0, age_delta.days)
                
                # Bonus for very recent (Active Memory context)
                if days_old < 30:
                    score += 0.5
                elif days_old < 90:
                    score += 0.3
                elif days_old < 365:
                    score += 0.1
                
                # Tie-breaker logic mainly, but here it's additive.
                # Also slight penalty for VERY old facts? 
                # No, just bonus for recent.

            ranked_facts.append((f, score))
            
        # Sort: Score DESC, ValidFrom DESC, ID DESC
        ranked_facts.sort(key=lambda x: (x[1], x[0].valid_from or datetime.min, x[0].id), reverse=True)
        
        # Format Results with Deduplication and Cleanup
        from difflib import SequenceMatcher
        from app.models.fact import Fact
        from sqlalchemy import update

        results = []
        seen_facts = [] # List of {'text': str, 'valid_from': datetime}
        facts_to_supersede = []
        
        for f, score in ranked_facts[:top_k * 2]:
            text = f"{f.subject} {f.predicate} {f.object}"
            norm_text = text.lower().strip()
            
            if f.valid_from:
                local_dt = f.valid_from.astimezone()
                date_str = local_dt.strftime('%Y-%m-%d')
                text += f" (This event took place on {date_str})"
            
            # Fuzzy Deduplication Check
            is_duplicate = False
            for seen in seen_facts:
                # Check 1: Exact Date Match (as requested)
                if seen['valid_from'] == f.valid_from:
                    # Check 2: Content Match > 90%
                    similarity = SequenceMatcher(None, norm_text, seen['norm_text']).ratio()
                    if similarity > 0.9:
                        is_duplicate = True
                        facts_to_supersede.append(f.id)
                        break
            
            if is_duplicate:
                continue
                
            seen_facts.append({
                'text': text, 
                'norm_text': norm_text,
                'valid_from': f.valid_from
            })
            
            if len(results) >= top_k:
                # If we filled the quota, subsequent items are just dropped, NOT superseded (we haven't compared them fully)
                # Actually, duplicate detection relies on seeing the "better" one first.
                # Since we sorted by Score, we kept the best.
                # Remaining items in ranked_facts (beyond loop) are ignored.
                break

            results.append({
                "text": text,
                "score": score,
                "metadata": {
                    "type": "fact",
                    "fact_id": f.id,
                    "confidence": f.confidence,
                    "valid_from": str(f.valid_from),
                    "semantic_match": f.id in semantic_fact_ids
                },
                "chunk": f.chunk
            })
            
        # Passive Cleanup: Mark duplicates as superseded
        if facts_to_supersede:
             print(f"Retrieval Cleanup: Marking {len(facts_to_supersede)} redundant facts as superseded.")
             try:
                 stmt = update(Fact).where(Fact.id.in_(facts_to_supersede)).values(is_superseded=True)
                 await db.execute(stmt)
                 await db.commit()
             except Exception as e:
                 print(f"Cleanup Failed: {e}")

        return results

    async def _search_episodic(self, query: str, user_id: int, db: AsyncSession, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search Memories primarily by time/recency matching query constraints?
        For now: Keyword search on Memories, sorted by created_at DESC.
        """
        from app.models.memory import Memory
        from sqlalchemy import text # For full text if available or simple like
        
        # Naive: Just simple LIKE query
        stmt = select(Memory).where(
            Memory.user_id == user_id, 
            Memory.content.ilike(f"%{query}%")
        ).order_by(Memory.created_at.desc()).limit(top_k)
        
        result = await db.execute(stmt)
        memories = result.scalars().all()
        
        results = []
        for m in memories:
            results.append({
                "text": m.content,
                "score": 1.0, # Valid hit
                "metadata": {
                    "type": "memory",
                    "memory_id": m.id,
                    "created_at": str(m.created_at),
                    "title": m.title
                },
                "chunk": None
            })
        return results

    async def _search_semantic(self, query: str, user_id: int, db: AsyncSession, top_k: int = 5, pre_fetched: Dict = None) -> List[Dict[str, Any]]:
        # 1. Fetch Candidates (or use pre-fetched)
        fetch_k = top_k * 10
        
        if pre_fetched:
            results = pre_fetched
        else:
            # 2. Vector Search (with embeddings for MMR)
            results = await vector_store.query(
                query, 
                n_results=fetch_k, 
                where={"user_id": user_id},
                include_values=True # Required for MMR
            )
        
        if not results.get("ids") or not results["ids"][0]:
            return []
            
        # Extract candidates
        # Flattening the list of lists since pinecone query returns [results_for_query_1, ...]
        candidate_ids = results["ids"][0]
        candidate_embeddings = results["embeddings"][0]
        candidate_metadatas = results["metadatas"][0]
        # Distances from vector DB (Cosine Distance? Or Similarity?)
        # Pinecone usually returns Cosine Similarity if configured with 'cosine'
        # But let's assume 'distances' field exists and represents relevance.
        # If not, we might need to re-compute query-doc similarity if query embedding isn't available.
        candidate_distances = results["distances"][0] if results.get("distances") else [0.0] * len(candidate_ids)
        candidate_docs = results["documents"][0] if results.get("documents") else [""] * len(candidate_ids)
        
        # 3. Vectorized MMR Implementation
        import numpy as np

        if not candidate_embeddings:
            # Fallback if no embeddings
            return []

        # Convert to numpy
        # Shape: (N, D)
        embeddings_np = np.array(candidate_embeddings)
        N, D = embeddings_np.shape
        
        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(embeddings_np, axis=1, keepdims=True)
        embeddings_norm = embeddings_np / (norms + 1e-10) # Avoid div/0
        
        # Calculate Severity Matrix (Sim between all candidates)
        # Shape: (N, N)
        similarity_matrix = np.dot(embeddings_norm, embeddings_norm.T)
        
        # Relevance Scores
        # If candidate_distances are Cosine Similarity, use them directly.
        # Ensure they are numpy array
        relevance_scores = np.array(candidate_distances)
        
        # Selection Loop
        selected_indices = []
        candidate_indices = list(range(N))
        
        lambda_mult = 0.7 
        
        seen_texts = set()
        
        # Pre-filter duplicates (Soft Dedupe)
        # We can mask out duplicates by setting their relevance to -inf
        mask_valid = np.ones(N, dtype=bool)
        
        for i in range(N):
            text = candidate_docs[i].strip() if candidate_docs[i] else ""
            # Simple hash check or short snippet check
            # For speed, strictly check if we've seen this exact text
            if text in seen_texts:
                 mask_valid[i] = False
            else:
                 seen_texts.add(text)
        
        # Main MMR Loop
        for _ in range(min(top_k, N)):
            if len(selected_indices) >= top_k:
                break
                
            # Current unselected valid candidates
            # We want to find i that maximizes MMR
            
            # Mask of currently unselected AND valid items
            candidate_mask = mask_valid.copy()
            candidate_mask[selected_indices] = False
            
            if not np.any(candidate_mask):
                break
                
            # Compute Max Sim to Selected for all unselected items
            # Shape: (N,) - but we only care about masked ones
            max_sim_to_selected = np.zeros(N)
            
            if selected_indices:
                # similarity_matrix[:, selected_indices] -> Shape (N, len(selected))
                # Max across the selected dimension
                sim_to_sel = similarity_matrix[:, selected_indices]
                max_sim_to_selected = np.max(sim_to_sel, axis=1)
                
            # MMR Score = lambda * Rel - (1-lambda) * MaxSim
            # We compute for ALL, but only pick from masked
            mmr_scores = (lambda_mult * relevance_scores) - ((1 - lambda_mult) * max_sim_to_selected)
            
            # Apply mask (set invalid/selected to -inf)
            mmr_scores[~candidate_mask] = -float('inf')
            
            best_idx = np.argmax(mmr_scores)
            
            if mmr_scores[best_idx] == -float('inf'):
                break # No more valid candidates
                
            selected_indices.append(best_idx)
            
        # 4. Fetch Rich Metadata & Format
        top_ids = [candidate_ids[i] for i in selected_indices]
        
        # Async fetch with Eager Loading (Same as before)
        query_stmt = (
            select(Chunk)
            .options(selectinload(Chunk.memory), selectinload(Chunk.document))
            .where(Chunk.embedding_id.in_(top_ids))
        )
        db_res = await db.execute(query_stmt)
        chunks = db_res.scalars().all()
        chunk_map = {c.embedding_id: c for c in chunks}
        
        formatted_results = []
        
        for i in selected_indices:
            emb_id = candidate_ids[i]
            base_score = float(relevance_scores[i])
            
            chunk = chunk_map.get(emb_id)
            
            if chunk:
                # Re-ranking logic
                feedback_mod = 1 + (chunk.feedback_score or 0.0)
                trust_mod = chunk.trust_score or 0.5
                
                # Recency Logic
                recency_mod = 1.0
                created_at = None
                if chunk.memory: created_at = chunk.memory.created_at
                elif chunk.document: created_at = chunk.document.created_at
                
                if created_at:
                    if created_at.tzinfo is None:
                        created_at = created_at.replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    days_diff = (now - created_at).days
                    recency_mod = 1 + (0.1 / max(1, days_diff))
                
                final_score = base_score * feedback_mod * (0.5 + trust_mod) * recency_mod
                
                meta = candidate_metadatas[i]
                meta["summary"] = chunk.summary
                meta["generated_qas"] = chunk.generated_qas
                meta["trust_score"] = chunk.trust_score
                if chunk.memory_id:
                    meta["memory_id"] = chunk.memory_id
                    # Clean up vector store artifacts if any
                    if "document_id" in meta: del meta["document_id"]
                elif chunk.document_id:
                    meta["document_id"] = chunk.document_id
                    if "memory_id" in meta: del meta["memory_id"]

                meta["chunk_id"] = chunk.id
                meta["recency_boost"] = round(recency_mod, 2)
                
                display_text = chunk.text
                if created_at:
                    display_date = created_at.strftime('%Y-%m-%d')
                    display_text += f"\n(This session took place on {display_date})"

                formatted_results.append({
                    "text": display_text, 
                    "score": final_score,
                    "metadata": meta,
                    "chunk": chunk
                })
            else:
                # Fallback
                meta = candidate_metadatas[i]
                formatted_results.append({
                    "text": candidate_docs[i],
                    "score": base_score,
                    "metadata": meta,
                    "chunk": None
                })
                
        # Sort by final score desc
        formatted_results.sort(key=lambda x: x["score"], reverse=True)
        
        return formatted_results

retrieval_service = RetrievalService()

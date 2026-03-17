"""
EngramMemoryStore — Drop-in replacement for Hermes MemoryStore.

Keeps the original MEMORY.md/USER.md interface (Hermes compatible) but adds
Engram cognitive memory as the primary long-term storage layer.

How it works:
1. Built-in MEMORY.md (2,200 chars) → "working memory" / quick-access essentials
2. Engram DB (unlimited) → "long-term memory" with cognitive retrieval
3. Every add() also stores in Engram for durable recall
4. New actions: recall, consolidate, forget, links, stats
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional

from engram import Memory as EngramMemory

logger = logging.getLogger(__name__)

# Import the original MemoryStore for delegation
import sys
HERMES_DIR = os.path.expanduser("~/.hermes/hermes-agent")
if HERMES_DIR not in sys.path:
    sys.path.insert(0, HERMES_DIR)

from tools.memory_tool import MemoryStore, ENTRY_DELIMITER

# Default Engram DB path
ENGRAM_DB = os.environ.get("ENGRAM_DB_PATH", os.path.expanduser("~/.hermes/engram.db"))


class EngramMemoryStore(MemoryStore):
    """
    Extended MemoryStore that backs all memories with Engram cognitive storage.
    
    Hermes still uses MEMORY.md/USER.md for system prompt injection (fast, bounded).
    But every memory also goes into Engram for long-term cognitive retrieval with
    ACT-R activation, Hebbian learning, and Ebbinghaus decay.
    """

    def __init__(self, memory_char_limit: int = 2200, user_char_limit: int = 1375,
                 engram_db: str = None):
        super().__init__(memory_char_limit, user_char_limit)
        db_path = engram_db or ENGRAM_DB
        
        # Initialize Engram with optional embedding auto-detection
        embedding = None
        embedding_config = os.environ.get("ENGRAM_EMBEDDING", "auto").lower()
        
        try:
            from engram.provider_detection import get_provider_with_fallback
            provider, model, reason = get_provider_with_fallback(embedding_config)
            
            if provider == "sentence-transformers":
                from engram.embeddings import SentenceTransformerAdapter
                embedding = SentenceTransformerAdapter(model)
            elif provider == "ollama":
                from engram.embeddings import OllamaAdapter
                embedding = OllamaAdapter(model=model)
            elif provider == "openai":
                from engram.embeddings import OpenAIAdapter
                embedding = OpenAIAdapter()
                
            logger.info(f"Engram initialized with {provider or 'FTS5-only'} ({reason})")
        except Exception as e:
            logger.warning(f"Engram embedding init failed: {e}, using FTS5-only")
        
        self._engram = EngramMemory(db_path, embedding=embedding)
        logger.info(f"EngramMemoryStore initialized: {db_path}")

    def add(self, target: str, content: str) -> Dict[str, Any]:
        """Add to both MEMORY.md and Engram."""
        # Original MEMORY.md add
        result = super().add(target, content)
        
        # Also store in Engram (even if MEMORY.md is full, Engram has no limit)
        try:
            mem_type = "relational" if target == "user" else "semantic"
            mid = self._engram.add(content, type=mem_type, importance=0.7,
                                    source=f"hermes:{target}")
            if result.get("success"):
                result["engram_id"] = mid
                result["engram_stored"] = True
            else:
                # MEMORY.md was full, but Engram stored it anyway
                result["engram_stored"] = True
                result["engram_id"] = mid
                result["engram_note"] = (
                    "Memory exceeded MEMORY.md limit but was stored in Engram "
                    "long-term memory. It won't appear in the system prompt but "
                    "can be recalled with action='recall'."
                )
        except Exception as e:
            logger.error(f"Engram store failed: {e}")
            result["engram_stored"] = False
            result["engram_error"] = str(e)
        
        return result

    def recall(self, query: str, limit: int = 5, types: list = None,
               min_confidence: float = 0.0) -> Dict[str, Any]:
        """Recall from Engram cognitive memory."""
        try:
            results = self._engram.recall(query, limit=limit, types=types,
                                           min_confidence=min_confidence)
            return {
                "success": True,
                "results": [
                    {
                        "id": r["id"],
                        "content": r["content"],
                        "type": r.get("type", r.get("memory_type", "?")),
                        "confidence": r.get("confidence", 0),
                        "confidence_label": r.get("confidence_label", ""),
                        "strength": r.get("strength", 0),
                        "age_days": r.get("age_days", 0),
                    }
                    for r in results
                ],
                "query": query,
                "count": len(results),
            }
        except Exception as e:
            logger.error(f"Engram recall failed: {e}")
            return {"success": False, "error": str(e)}

    def consolidate(self, days: float = 1.0) -> Dict[str, Any]:
        """Run Engram consolidation — strengthen important memories, decay others."""
        try:
            self._engram.consolidate(days=days)
            stats = self._engram.stats()
            return {
                "success": True,
                "message": "Consolidation complete.",
                "stats": {
                    "total_memories": stats["total_memories"],
                    "layers": stats["layers"],
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def forget_engram(self, memory_id: str = None, threshold: float = 0.01) -> Dict[str, Any]:
        """Forget a specific memory or prune weak ones."""
        try:
            self._engram.forget(memory_id=memory_id, threshold=threshold)
            return {"success": True, "message": "Memory forgotten."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def engram_stats(self) -> Dict[str, Any]:
        """Get Engram memory statistics."""
        try:
            stats = self._engram.stats()
            return {"success": True, "stats": stats}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def hebbian_links(self, memory_id: str) -> Dict[str, Any]:
        """Get Hebbian associations for a memory."""
        try:
            from engram.hebbian import get_hebbian_neighbors
            neighbor_ids = get_hebbian_neighbors(self._engram._store, memory_id)
            links = []
            for nid in neighbor_ids:
                entry = self._engram._store.get(nid)
                if entry:
                    links.append({
                        "id": nid,
                        "content": entry.content[:100] + "..." if len(entry.content) > 100 else entry.content,
                    })
            return {"success": True, "source_id": memory_id, "links": links}
        except Exception as e:
            return {"success": False, "error": str(e)}


def engram_memory_tool(
    action: str,
    target: str = "memory",
    content: str = None,
    old_text: str = None,
    query: str = None,
    limit: int = 5,
    memory_id: str = None,
    store: Optional[EngramMemoryStore] = None,
) -> str:
    """Extended memory tool with Engram cognitive actions."""
    if store is None:
        return json.dumps({"success": False, "error": "Memory not available."}, ensure_ascii=False)

    # Original actions → delegate to MemoryStore
    if action in ("add", "replace", "remove"):
        if action == "add":
            if not content:
                return json.dumps({"success": False, "error": "Content required."}, ensure_ascii=False)
            result = store.add(target, content)
        elif action == "replace":
            if not old_text or not content:
                return json.dumps({"success": False, "error": "old_text and content required."}, ensure_ascii=False)
            result = store.replace(target, old_text, content)
        elif action == "remove":
            if not old_text:
                return json.dumps({"success": False, "error": "old_text required."}, ensure_ascii=False)
            result = store.remove(target, old_text)
        return json.dumps(result, ensure_ascii=False, default=str)

    # Engram-specific actions
    if action == "recall":
        result = store.recall(query or content or "", limit=limit)
    elif action == "consolidate":
        result = store.consolidate()
    elif action == "forget":
        result = store.forget_engram(memory_id=memory_id)
    elif action == "links":
        if not memory_id:
            return json.dumps({"success": False, "error": "memory_id required."}, ensure_ascii=False)
        result = store.hebbian_links(memory_id)
    elif action == "stats":
        result = store.engram_stats()
    else:
        return json.dumps({"success": False, "error": f"Unknown action '{action}'."}, ensure_ascii=False)

    return json.dumps(result, ensure_ascii=False, default=str)


# Extended schema for the memory tool
ENGRAM_MEMORY_SCHEMA = {
    "name": "memory",
    "description": (
        "Persistent memory with neuroscience-grounded cognitive retrieval.\n\n"
        "BASIC ACTIONS (Hermes-compatible):\n"
        "- add: Save to MEMORY.md + Engram long-term memory\n"
        "- replace: Update an entry in MEMORY.md\n"
        "- remove: Delete an entry from MEMORY.md\n\n"
        "COGNITIVE ACTIONS (Engram-powered):\n"
        "- recall: Retrieve memories using ACT-R activation scoring (recency × frequency × importance)\n"
        "- consolidate: Run memory maintenance — strengthen important memories, decay unused ones\n"
        "- forget: Remove a specific memory or prune all weak memories\n"
        "- links: Show Hebbian associations (memories that are recalled together become linked)\n"
        "- stats: Memory system health and metrics\n\n"
        "WHEN TO USE:\n"
        "- add: User shares preferences, corrections, environment facts\n"
        "- recall: Before answering — check what you already know. Use 'query' param.\n"
        "- consolidate: Periodically, to maintain memory quality\n"
        "- MEMORY.md is limited (2,200 chars) but Engram has NO limit. When MEMORY.md is full,\n"
        "  memories still go to Engram and can be recalled."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["add", "replace", "remove", "recall", "consolidate", "forget", "links", "stats"],
                "description": "The action to perform."
            },
            "target": {
                "type": "string",
                "enum": ["memory", "user"],
                "description": "Which store: 'memory' for notes, 'user' for user profile. (For add/replace/remove)"
            },
            "content": {
                "type": "string",
                "description": "Entry content (add/replace) or query text (recall)."
            },
            "old_text": {
                "type": "string",
                "description": "Substring to identify entry for replace/remove."
            },
            "query": {
                "type": "string",
                "description": "Search query for recall action."
            },
            "limit": {
                "type": "integer",
                "description": "Max results for recall (default: 5)."
            },
            "memory_id": {
                "type": "string",
                "description": "Memory ID for forget/links actions."
            },
        },
        "required": ["action"],
    },
}

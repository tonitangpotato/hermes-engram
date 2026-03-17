---
name: engramai
description: "Cognitive memory powered by neuroscience — ACT-R activation, Hebbian learning, Ebbinghaus forgetting. Replaces flat memory with a brain-like system that learns, forgets, and discovers associations."
version: 1.0.0
metadata:
  hermes:
    tags: [memory, cognitive-science, neuroscience, ai-agents]
    category: memory
    emoji: "🧠"
    requires:
      bins: [python3]
      packages:
        pip: [engramai]
---

# Engram — Cognitive Memory for Hermes Agent 🧠

## When to Use
- When you need to remember something important across sessions
- When recalling past conversations, preferences, or facts
- When the built-in MEMORY.md (2,200 chars) is full or insufficient
- When you want to find connections between memories you didn't explicitly link
- Automatically: store important facts after every conversation, recall relevant memories before answering

## What It Is
Engram is a neuroscience-grounded memory system implementing:
- **ACT-R activation** (Anderson 1993) — memories that are used more often and more recently are easier to recall
- **Hebbian learning** (Hebb 1949) — memories recalled together become linked ("neurons that fire together wire together")
- **Ebbinghaus forgetting curve** (1885) — unused memories naturally decay, keeping retrieval clean
- **Memory consolidation** — important working memories graduate to durable core storage

## Procedure

### Store a memory
```bash
python3 -c "
from engram import Memory
mem = Memory('~/.hermes/engram.db')
mem.add('CONTENT_HERE', type='TYPE', importance=0.7)
"
```
Types: `semantic`, `episodic`, `procedural`, `causal`, `relational`
Importance: 0.0 (trivial) to 1.0 (critical)

### Recall memories
```bash
python3 -c "
from engram import Memory
mem = Memory('~/.hermes/engram.db')
results = mem.recall('QUERY_HERE', limit=5)
for r in results:
    print(f'[{r[\"memory_type\"]}] (score: {r[\"score\"]:.2f}) {r[\"content\"]}')
"
```

### Run consolidation (periodic maintenance)
```bash
python3 -c "
from engram import Memory
mem = Memory('~/.hermes/engram.db')
mem.consolidate()
print('Consolidation complete')
"
```

### Get memory stats
```bash
python3 -c "
from engram import Memory
mem = Memory('~/.hermes/engram.db')
stats = mem.stats()
for k, v in stats.items():
    print(f'{k}: {v}')
"
```

## Best Practices
1. **Store after every meaningful conversation** — preferences, facts, corrections, project context
2. **Recall before answering** — check if you already know something relevant
3. **Use appropriate types** — `episodic` for events, `semantic` for facts, `procedural` for how-tos, `relational` for connections between things
4. **Set importance** — 0.9+ for critical facts (allergies, passwords, deadlines), 0.3-0.5 for general context
5. **Run consolidation daily** — strengthens important memories, lets unimportant ones decay
6. **Don't duplicate built-in memory** — use Engram for overflow and long-term storage, MEMORY.md for quick-access essentials

## How It's Different from Built-in Memory
| Feature | Built-in MEMORY.md | Engram |
|---------|-------------------|--------|
| Capacity | 2,200 chars | Unlimited |
| Search | None (full inject) | FTS5 + Hebbian + optional embeddings |
| Forgetting | Manual delete | Automatic decay (Ebbinghaus) |
| Associations | None | Automatic Hebbian links |
| Activation | None | ACT-R (recency × frequency) |
| Cross-session | Yes (frozen snapshot) | Yes (live query) |

## Pitfalls
- Don't store trivial info (agent will remember "user said hi" — not useful)
- Don't store raw data dumps (large code blocks should go in files, not memory)
- Consolidation is needed periodically or memory quality degrades
- First recall in a new session is slightly slower (DB warm-up)

## Verification
After storing: recall with a related query and confirm the memory appears.
Check stats to see total memories, types distribution, and Hebbian link count.

# 🧠 Hermes × Engram: Cognitive Memory for Hermes Agent

> Give your Hermes Agent a brain that learns, forgets, and discovers connections — powered by neuroscience.

## The Problem

Hermes Agent's built-in memory is a **2,200-character text file**. That's about 15 bullet points. When it fills up, the agent deletes old memories to make room. There's no search, no prioritization, no associations between memories.

**Real brains don't work like text files.**

## The Solution

Engram integrates as a **native MCP server**, giving Hermes 20+ cognitive memory tools:

| Tool | What It Does |
|------|-------------|
| `store` | Save a memory with type + importance |
| `recall` | Retrieve memories ranked by cognitive activation |
| `session_recall` | Smart recall that skips redundant queries (saves 70-80% API calls) |
| `consolidate` | Strengthen important memories, decay unimportant ones |
| `forget` | Actively prune weak/outdated memories |
| `reward` | Dopaminergic feedback signal adjusts memory weights |
| `hebbian_links` | View auto-discovered associations between memories |
| `pin` / `unpin` | Protect critical memories from decay |
| `stats` | Memory system health and metrics |

Built on 4 neuroscience models:

| Model | What It Does | Citation |
|-------|-------------|----------|
| **ACT-R Activation** | Memories used more often and more recently are easier to recall | Anderson, 1993 |
| **Hebbian Learning** | Memories recalled together become linked automatically | Hebb, 1949 |
| **Ebbinghaus Forgetting** | Unused memories decay naturally, keeping retrieval clean | Ebbinghaus, 1885 |
| **Memory Consolidation** | Important short-term memories become durable long-term storage | Murre & Chessa, 2011 |

## Integration: Deep (Source-Level)

Engram replaces Hermes's `MemoryStore` class directly — **no MCP overhead, no CLI wrappers**. The `memory` tool gains cognitive actions natively.

### Install

```bash
git clone https://github.com/tonitangpotato/hermes-engram
cd hermes-engram
./install.sh
```

This:
1. Installs `engramai` package
2. Drops `EngramMemoryStore` into Hermes's tools directory
3. Patches `run_agent.py` to use it instead of the default `MemoryStore`
4. Backs up originals (safe to revert)

### What Changes

The `memory` tool gains new actions:

```
memory(action="recall", query="user preferences")     → ACT-R scored retrieval
memory(action="consolidate")                           → strengthen/decay cycle
memory(action="forget", memory_id="abc123")            → active forgetting
memory(action="links", memory_id="abc123")             → Hebbian associations
memory(action="stats")                                 → memory health metrics
```

Original actions (`add`, `replace`, `remove`) still work exactly as before — but now every `add` also stores in Engram for unlimited long-term memory.

### Alternative: MCP Server

If you prefer not to patch Hermes source, add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  engram:
    command: python3
    args: ["-m", "engram.mcp_server"]
    env:
      ENGRAM_DB_PATH: "~/.hermes/engram.db"
```

## Before vs After

| Feature | Built-in MEMORY.md | With Engram |
|---------|-------------------|-------------|
| Capacity | 2,200 chars | **Unlimited** |
| Search | None (full inject) | **FTS5 + Hebbian + embeddings** |
| Forgetting | Manual delete | **Automatic cognitive decay** |
| Associations | None | **Auto-discovered Hebbian links** |
| Activation | None | **ACT-R (recency × frequency × importance)** |
| Session awareness | Frozen snapshot | **Live query with working memory model** |
| Cost per recall | Full context injection | **$0 (local SQLite)** |

## Production Stats

This isn't a prototype. Engram has been running in production for 30+ days:

- **5,537** memories stored
- **26,654** Hebbian associations formed automatically  
- **520,279** successful recalls
- **$0** inference cost

## Architecture

```
Hermes Agent
    ↓ MCP protocol (stdio)
Engram MCP Server (20 tools)
    ├── FTS5 full-text search
    ├── Hebbian co-activation graph
    ├── ACT-R activation scoring
    ├── Ebbinghaus decay curves
    ├── Session working memory (Miller's Law)
    ├── Emotional bus + flashbulb memory
    ├── Memory consolidation pipeline
    └── SQLite (local, private, zero-cost)
```

## Visualization: Engram Pensieve ✨

> *"I use the Pensieve. One simply siphons the excess thoughts from one's mind, pours them into the basin, and examines them at one's leisure."* — Dumbledore

Included: a React + D3.js force-directed graph visualizer for the memory network.

```bash
cd pensieve && ./run.sh
# Open http://localhost:5173
```

- Each orb = a memory (size = activation strength, color = type)
- Lines between orbs = Hebbian associations
- Fading orbs = decaying memories
- Click to inspect any memory's full content + linked memories

## About

Built by [@horseonedragon](https://x.com/horseonedragon) — neuroscience background (Shanghai Tech, Oxford, Yale), Amazon AI engineer, building cognitive AI systems.

- **Engram**: [github.com/tonitangpotato/engram-ai](https://github.com/tonitangpotato/engram-ai)
- **License**: MIT
- **Privacy**: All data stays local. No API calls required. No cloud dependency.

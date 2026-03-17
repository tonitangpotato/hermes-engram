#!/bin/bash
# Install Engram cognitive memory into Hermes Agent
set -e

HERMES_DIR="${HERMES_HOME:-$HOME/.hermes}"
HERMES_AGENT="$HERMES_DIR/hermes-agent"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🧠 Installing Engram cognitive memory for Hermes Agent..."
echo ""

# 1. Check prerequisites
if ! command -v hermes &> /dev/null; then
    echo "❌ Hermes Agent not found. Install it first:"
    echo "   curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash"
    exit 1
fi

if ! python3 -c "from engram import Memory" 2>/dev/null; then
    echo "📦 Installing engramai..."
    pip3 install engramai
fi

# 2. Copy EngramMemoryStore to Hermes tools
echo "📁 Installing EngramMemoryStore..."
cp "$SCRIPT_DIR/src/engram_memory_store.py" "$HERMES_AGENT/tools/"

# 3. Backup original memory_tool.py
if [ ! -f "$HERMES_AGENT/tools/memory_tool.py.orig" ]; then
    cp "$HERMES_AGENT/tools/memory_tool.py" "$HERMES_AGENT/tools/memory_tool.py.orig"
    echo "💾 Backed up original memory_tool.py"
fi

# 4. Patch run_agent.py to use EngramMemoryStore
AGENT_PY="$HERMES_AGENT/run_agent.py"
if grep -q "EngramMemoryStore" "$AGENT_PY" 2>/dev/null; then
    echo "✅ Already patched!"
else
    echo "🔧 Patching run_agent.py to use EngramMemoryStore..."
    # Replace MemoryStore import with EngramMemoryStore
    sed -i.bak 's/from tools\.memory_tool import MemoryStore/try:\n                        from tools.engram_memory_store import EngramMemoryStore as MemoryStore\n                    except ImportError:\n                        from tools.memory_tool import MemoryStore/' "$AGENT_PY"
    echo "✅ Patched!"
fi

# 5. Install MCP server config (as backup integration)
if ! grep -q "engram" "$HERMES_DIR/config.yaml" 2>/dev/null; then
    echo "📝 Note: You can also add Engram as MCP server in ~/.hermes/config.yaml:"
    echo "   mcp_servers:"
    echo "     engram:"
    echo "       command: python3"
    echo "       args: [\"-m\", \"engram.mcp_server\"]"
    echo "       env:"
    echo "         ENGRAM_DB_PATH: \"~/.hermes/engram.db\""
fi

# 6. Copy skill (supplementary)
if [ -d "$SCRIPT_DIR/skill/engramai" ]; then
    cp -r "$SCRIPT_DIR/skill/engramai" "$HERMES_DIR/skills/"
    echo "📚 Installed engramai skill"
fi

echo ""
echo "✨ Engram cognitive memory installed!"
echo ""
echo "   Engram DB: ~/.hermes/engram.db"
echo "   Hermes memory tool now has cognitive actions:"
echo "   - recall: ACT-R activation retrieval"
echo "   - consolidate: memory maintenance"
echo "   - forget: prune weak memories"
echo "   - links: Hebbian associations"
echo "   - stats: memory health metrics"
echo ""
echo "   Start Hermes normally: hermes chat"

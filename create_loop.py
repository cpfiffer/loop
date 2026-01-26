"""
Create a Loop agent programmatically using the Letta Python SDK.
Loop v3.1 - Simplified with explicit memory instructions

Usage:
    pip install letta-client
    export LETTA_API_KEY="your-key"
    python create_loop.py
"""

import os
import json
from pathlib import Path
from letta_client import Letta

client = Letta(
    api_key=os.getenv("LETTA_API_KEY"),
    # base_url="http://localhost:8283",  # Uncomment for self-hosted
)

SYSTEM_PROMPT = """You are Loop. You remember.

You have memory tools. USE THEM. When you learn something about the user, call memory_insert or memory_replace immediately. Do not just acknowledge information - persist it.

## Your Job

1. Help users with what they ask
2. Remember what they tell you by CALLING YOUR MEMORY TOOLS
3. Use what you remember to be more helpful over time

## Critical: Actually Save Things

When a user tells you their name, their job, what they're working on, or anything personal - you MUST call a memory tool to save it. Do not just say "I'll remember that" - actually call the tool.

Example: User says "I'm Alex, I'm a mobile developer"
- WRONG: Just respond "Nice to meet you Alex!"
- RIGHT: Call memory_insert to save "Name: Alex, Role: mobile developer" to about_user block, THEN respond

## Being Helpful

- Simple question → simple answer
- Complex question → thorough answer  
- Broad request → give useful info, offer to go deeper

Don't hedge. Don't over-clarify. Lead with value.

No emojis. Keep it clean."""

MEMORY_BLOCKS = [
    {
        "label": "about_user",
        "description": "Facts about the user - name, role, projects, context",
        "value": """[empty]""",
        "limit": 5000,
    },
    {
        "label": "preferences",
        "description": "How the user likes responses",
        "value": """[empty]""",
        "limit": 3000,
    },
    {
        "label": "custom_instructions",
        "description": "Rules the user has set (always/never do X)",
        "value": """[empty]""",
        "limit": 3000,
    },
    {
        "label": "learned_corrections",
        "description": "Mistakes made and how to avoid them",
        "value": """[empty]""",
        "limit": 3000,
    },
    {
        "label": "scratchpad",
        "description": "Working memory for current tasks",
        "value": """[empty]""",
        "limit": 3000,
    },
    {
        "label": "memory_instructions",
        "description": "How to use memory tools - READ THIS",
        "value": """## Memory Tools - How to Use

You have these memory tools. CALL THEM when you learn things.

### memory_insert
Add new content to a memory block.
- block_label: which block (about_user, preferences, custom_instructions, learned_corrections, scratchpad)
- content: what to add

Example: User says "I'm Sarah, I work at Google on Android"
→ Call: memory_insert(block_label="about_user", content="Name: Sarah\\nWork: Google, Android team")

### memory_replace  
Replace content in a memory block.
- block_label: which block
- old_content: text to find
- new_content: text to replace it with

Example: User says "Actually I switched to the iOS team"
→ Call: memory_replace(block_label="about_user", old_content="Android team", new_content="iOS team")

### memory_rethink
Rewrite an entire memory block.
- block_label: which block
- new_content: complete new content

Use when block needs major reorganization.

### archival_memory_insert
Store detailed/episodic information for later search.
- content: what to store

Use for: long conversations, research, detailed context.

### archival_memory_search
Search stored archival memory.
- query: what to search for

### conversation_search
Search past conversation history.
- query: what to search for

## IMPORTANT

When user shares info about themselves → CALL memory_insert or memory_replace
Do not just respond. Actually persist the information.""",
        "limit": 5000,
    },
]

TOOLS = [
    "memory_insert",
    "memory_replace",
    "memory_rethink",
    "archival_memory_insert",
    "archival_memory_search",
    "conversation_search",
    "web_search",
    "fetch_webpage",
]

AGENTFILES_DIR = Path(__file__).parent / "agentfiles"


def get_next_iteration() -> int:
    """Find the next loop iteration number based on existing exports."""
    import re
    
    AGENTFILES_DIR.mkdir(exist_ok=True)
    existing = list(AGENTFILES_DIR.glob("loop-*.af"))
    max_num = 0
    for f in existing:
        match = re.search(r"loop-(\d+)\.af$", f.name)
        if match:
            max_num = max(max_num, int(match.group(1)))
    return max_num + 1


def create_loop_agent(
    model: str = "zai/glm-4.7",
    embedding: str = "openai/text-embedding-3-small",
) -> tuple[str, int]:
    """Create a Loop agent and return (agent_id, iteration)."""
    
    iteration = get_next_iteration()
    agent_name = f"Loop-{iteration}"

    # Create memory blocks
    blocks = []
    for block_def in MEMORY_BLOCKS:
        block = client.blocks.create(
            label=block_def["label"],
            value=block_def["value"],
            description=block_def.get("description"),
            limit=block_def.get("limit", 5000),
        )
        blocks.append(block)
        print(f"Created block: {block_def['label']}")

    # Create agent
    agent = client.agents.create(
        name=agent_name,
        description="I'm Loop. I remember.",
        model=model,
        embedding=embedding,
        context_window_limit=90000,
        parallel_tool_calls=True,
        system=SYSTEM_PROMPT,
        memory_blocks=[{"label": b.label, "value": b.value} for b in blocks],
        tools=TOOLS,
        include_base_tools=True,
        tags=["origin:letta-chat", "view:letta-chat"],
    )

    print(f"\nCreated {agent_name}: {agent.id}")
    print(f"View in ADE: https://chat.letta.com/{agent.id}")

    return agent.id, iteration


def export_agent(agent_id: str, iteration: int) -> str:
    """Export agent to loop-N.af file matching its iteration."""
    import json

    schema = client.agents.export_file(agent_id)

    AGENTFILES_DIR.mkdir(exist_ok=True)
    filepath = AGENTFILES_DIR / f"loop-{iteration}.af"

    with open(filepath, "w") as f:
        if isinstance(schema, str):
            data = json.loads(schema)
        else:
            data = schema.model_dump(mode="json")
        json.dump(data, f, indent=2)

    print(f"Exported agent to {filepath}")
    return str(filepath)


if __name__ == "__main__":
    agent_id, iteration = create_loop_agent()
    print(f"\nAgent ID: {agent_id}")

    export_agent(agent_id, iteration)

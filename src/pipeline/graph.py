from typing import Dict, Any
from datetime import datetime, timezone
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.pipeline.state import PipelineState
from src.agents.research import run_research_agent
from src.agents.script import run_script_agent


def research_node(state: PipelineState) -> Dict[str, Any]:
    """
    Research Agent Node
    Loads competitor ads dataset, ranks by longevity, persists raw ads to `ads` table,
    extracts copy-grounded marketing concepts, persists to `concepts` table,
    and updates Kanban state: Researching -> Analyzing.
    """
    client_id = state.get("client_id", "crowdwisdom")
    run_id = state.get("run_id", "run_stub")
    config_path = f"clients/{client_id}/config.yaml"

    print(f"--> [Node 1: Research Agent] Executing for client '{client_id}', run_id '{run_id}'...")

    research_res = run_research_agent(
        client_config_path=config_path,
        run_id=run_id
    )

    history = list(state.get("history") or [])
    history.append({
        "state": "Researching",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detail": f"Scraped & ranked {research_res['raw_ads_count']} competitor ads by longevity"
    })
    history.append({
        "state": "Analyzing",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detail": f"Extracted {len(research_res['concepts'])} grounded marketing concepts"
    })

    return {
        "kanban_state": "Analyzing",
        "raw_ads": research_res["ads"],
        "concepts": research_res["concepts"],
        "history": history,
    }


def script_node(state: PipelineState) -> Dict[str, Any]:
    """
    Script Agent Node
    Ingests proprietary data, uses OpenRouter model routing to generate 3 script variants (A, B, C),
    persists scripts to Supabase `scripts` table, and updates Kanban state: Writing Script -> Awaiting Approval.
    """
    client_id = state.get("client_id", "crowdwisdom")
    run_id = state.get("run_id", "run_stub")
    concepts = state.get("concepts", [])
    config_path = f"clients/{client_id}/config.yaml"

    print(f"--> [Node 2: Script Agent] Executing for client '{client_id}', run_id '{run_id}'...")

    script_res = run_script_agent(
        client_config_path=config_path,
        run_id=run_id,
        concepts=concepts
    )

    history = list(state.get("history") or [])
    history.append({
        "state": "Writing Script",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detail": "Generated script variants A (Pain Point), B (Proprietary Stat), and C (Product Solution)"
    })
    history.append({
        "state": "Awaiting Approval",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detail": "Paused at human approval gate before video rendering"
    })

    return {
        "kanban_state": "Awaiting Approval",
        "scripts": script_res["scripts"],
        "approval_status": "pending",
        "history": history,
    }


def video_node(state: PipelineState) -> Dict[str, Any]:
    """
    Video Agent Node (Stub for Step 5)
    Programmatically renders approved script into 30-60s video via Remotion + Edge-TTS.
    Kanban Lifecycle: Rendering Video -> Completed
    """
    client_id = state.get("client_id", "unknown")
    approved_script_id = state.get("approved_script_id", "none")
    print(f"--> [Node 3: Video Agent] Rendering video for approved script '{approved_script_id}'...")

    history = list(state.get("history") or [])
    history.append({
        "state": "Rendering Video",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detail": f"Rendering video for script {approved_script_id}"
    })
    history.append({
        "state": "Completed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detail": "Video rendered and uploaded to Supabase Storage"
    })

    return {
        "kanban_state": "Completed",
        "video_result": {
            "video_id": "vid_001",
            "script_id": approved_script_id,
            "video_url": f"https://srsystdngccekzlmpuym.supabase.co/storage/v1/object/public/videos/{client_id}/final.mp4",
            "duration_seconds": 45,
        },
        "history": history,
    }


def build_pipeline_graph():
    """
    Constructs the 3-agent stateful graph with human-in-the-loop approval checkpoint.
    """
    builder = StateGraph(PipelineState)

    builder.add_node("research_node", research_node)
    builder.add_node("script_node", script_node)
    builder.add_node("video_node", video_node)

    builder.add_edge(START, "research_node")
    builder.add_edge("research_node", "script_node")
    builder.add_edge("script_node", "video_node")
    builder.add_edge("video_node", END)

    memory = MemorySaver()

    # Pause before video_node for human approval gate
    return builder.compile(checkpointer=memory, interrupt_before=["video_node"])

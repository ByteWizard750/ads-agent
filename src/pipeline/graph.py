from typing import Dict, Any
from datetime import datetime, timezone
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.pipeline.state import PipelineState
from src.agents.research import run_research_agent
from src.agents.script import run_script_agent
from src.agents.video import run_video_agent


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
    Video Agent Node (Step 5)
    Programmatically renders approved script into 30-60s video via Remotion + Edge-TTS,
    uploads MP4 to Supabase Storage, and persists video record into `videos` table.
    Kanban Lifecycle: Rendering Video -> Completed
    """
    client_id = state.get("client_id", "crowdwisdom")
    run_id = state.get("run_id", "run_stub")
    approved_script_id = state.get("approved_script_id")
    config_path = f"clients/{client_id}/config.yaml"

    if not approved_script_id:
        # Fallback to approved script from state scripts if available
        scripts = state.get("scripts", [])
        for s in scripts:
            if s.get("approval_status") == "approved":
                approved_script_id = s.get("id")
                break
        if not approved_script_id and scripts:
            approved_script_id = scripts[1].get("id") if len(scripts) > 1 else scripts[0].get("id")

    print(f"--> [Node 3: Video Agent] Rendering vertical video for approved script '{approved_script_id}'...")

    video_res = run_video_agent(
        client_config_path=config_path,
        run_id=run_id,
        script_id=approved_script_id
    )

    history = list(state.get("history") or [])
    history.append({
        "state": "Rendering Video",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detail": f"Rendering Remotion vertical video for script {approved_script_id}"
    })
    history.append({
        "state": "Awaiting Video Approval",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detail": f"Video rendered and uploaded to Supabase Storage: {video_res['public_url']}"
    })

    return {
        "kanban_state": "Awaiting Video Approval",
        "video_result": video_res["video_record"],
        "video_approval_status": "pending",
        "history": history,
    }

def publish_node(state: PipelineState) -> Dict[str, Any]:
    """
    Publish Node (Step 7)
    Executes after human approves the rendered video inline.
    Marks the pipeline as Completed.
    """
    history = list(state.get("history") or [])
    history.append({
        "state": "Completed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detail": "Video approved for final publication"
    })

    return {
        "kanban_state": "Completed",
        "history": history,
    }


def build_pipeline_graph():
    """
    Constructs the 3-agent stateful graph with human-in-the-loop approval checkpoints.
    """
    builder = StateGraph(PipelineState)

    builder.add_node("research_node", research_node)
    builder.add_node("script_node", script_node)
    builder.add_node("video_node", video_node)
    builder.add_node("publish_node", publish_node)

    builder.add_edge(START, "research_node")
    builder.add_edge("research_node", "script_node")
    builder.add_edge("script_node", "video_node")
    builder.add_edge("video_node", "publish_node")
    builder.add_edge("publish_node", END)

    memory = MemorySaver()

    # Pause before video_node for Script Approval, and before publish_node for Video Approval
    return builder.compile(checkpointer=memory, interrupt_before=["video_node", "publish_node"])

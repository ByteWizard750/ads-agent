from typing import TypedDict, List, Dict, Any, Optional


class PipelineState(TypedDict):
    """
    State payload flowing through the LangGraph 3-agent pipeline.
    All states strictly scope execution by client_id and track Kanban lifecycle.
    """

    client_id: str
    run_id: str
    config: Dict[str, Any]

    # Kanban state tracked per run/script (must match kanban_status enum)
    kanban_state: str

    # Agent outputs
    raw_ads: List[Dict[str, Any]]
    concepts: List[Dict[str, Any]]
    scripts: List[Dict[str, Any]]

    # Human-in-the-loop approval gate state (Script)
    approved_script_id: Optional[str]
    approval_status: Optional[str]  # 'pending', 'approved', 'rejected'
    rejection_reason: Optional[str]

    # Human-in-the-loop approval gate state (Video)
    video_approval_status: Optional[str] # 'pending', 'approved', 'rejected'

    # Video output
    video_result: Optional[Dict[str, Any]]

    # Execution logging & history
    error: Optional[str]
    history: List[Dict[str, Any]]

"""
State schema extension for specialist agents middleware.

Adds specialist_histories field to track full conversation histories
for each specialist agent invocation.
"""

from typing import Annotated, NotRequired
from typing_extensions import TypedDict


def merge_specialist_histories(left: dict | None, right: dict) -> dict:
    """
    Merge specialist histories from concurrent updates.
    
    This reducer allows multiple specialists to update histories in parallel.
    """
    if left is None:
        return right
    return {**left, **right}


class SpecialistHistoriesState(TypedDict):
    """
    State extension for tracking specialist agent conversation histories.
    
    This mixin can be used with any agent state to add specialist tracking.
    The histories are stored with keys like "specialist_name_1", "specialist_name_2", etc.
    """
    
    specialist_histories: NotRequired[Annotated[dict[str, list], merge_specialist_histories]]
    """
    Full conversation histories for each specialist invocation.
    
    Keys are formatted as "{specialist_name}_{call_number}".
    Values are the full message lists from specialist agent executions.
    
    Uses Annotated with merge_specialist_histories reducer to support
    concurrent updates from multiple specialists.
    
    Example:
        {
            "risk_assessment_1": [HumanMessage(...), AIMessage(...), ...],
            "risk_assessment_2": [HumanMessage(...), AIMessage(...), ...],
            "supply_chain_1": [HumanMessage(...), AIMessage(...), ...]
        }
    """

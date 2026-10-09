from typing import List, Dict, Set, Tuple
import networkx as nx
from dataclasses import dataclass

@dataclass
class PrerequisiteEdge:
    skill_id: int
    prerequisite_skill_id: int
    relationship_strength: float = 1.0

@dataclass
class LearningPathStep:
    step_number: int
    skill_id: int
    skill_name: str
    status: str  # "SATISFIED", "IN_PROGRESS", "RECOMMENDED"
    current_level: float
    required_level: float
    prerequisites_satisfied: bool

def build_prerequisite_graph(edges: List[PrerequisiteEdge]) -> nx.DiGraph:
    """
    Build a Directed Graph representing skill prerequisites.
    Edge direction: prerequisite_skill_id -> skill_id
    (meaning prerequisite must be learned BEFORE skill)
    """
    G = nx.DiGraph()
    for edge in edges:
        G.add_edge(
            edge.prerequisite_skill_id, 
            edge.skill_id, 
            weight=edge.relationship_strength
        )
    return G

def detect_prerequisite_cycles(G: nx.DiGraph) -> List[List[int]]:
    """Detect cycles in prerequisite graph. Returns list of cycle nodes."""
    try:
        cycles = list(nx.simple_cycles(G))
        return cycles
    except Exception:
        return []

def generate_ordered_learning_path(
    prereq_edges: List[PrerequisiteEdge],
    skill_names: Dict[int, str],
    target_skill_gaps: Dict[int, Tuple[float, float]], # skill_id -> (current_level, required_level)
    student_satisfied_skills: Set[int]
) -> List[LearningPathStep]:
    """
    Generates a prerequisite-aware learning sequence for missing skill gaps.
    Sorts dependencies so prerequisite skills appear before downstream dependent skills.
    """
    G = build_prerequisite_graph(prereq_edges)
    
    # Check for cycles
    cycles = detect_prerequisite_cycles(G)
    if cycles:
        raise ValueError(f"Cycle detected in prerequisite graph: {cycles}")

    gap_skill_ids = set(target_skill_gaps.keys())
    
    # Perform topological sort on entire DAG
    try:
        topo_order = list(nx.topological_sort(G))
    except nx.NetworkXUnfeasible:
        raise ValueError("Prerequisite graph contains cycles and cannot be topologically sorted.")

    # Include skills in topological order, then any unconstrained gap skills
    ordered_skills: List[int] = []
    for s_id in topo_order:
        if s_id in gap_skill_ids and s_id not in ordered_skills:
            ordered_skills.append(s_id)
            
    for s_id in gap_skill_ids:
        if s_id not in ordered_skills:
            ordered_skills.append(s_id)

    learning_path: List[LearningPathStep] = []
    step_num = 1

    for s_id in ordered_skills:
        curr_lvl, req_lvl = target_skill_gaps[s_id]
        name = skill_names.get(s_id, f"Skill #{s_id}")

        # Check if direct prerequisites for this skill are satisfied
        prereqs = list(G.predecessors(s_id)) if G.has_node(s_id) else []
        all_prereqs_satisfied = all(p in student_satisfied_skills for p in prereqs)

        if curr_lvl >= req_lvl:
            status = "SATISFIED"
        elif all_prereqs_satisfied:
            status = "RECOMMENDED"
        else:
            status = "LOCKED_PREREQUISITE"

        learning_path.append(
            LearningPathStep(
                step_number=step_num,
                skill_id=s_id,
                skill_name=name,
                status=status,
                current_level=curr_lvl,
                required_level=req_lvl,
                prerequisites_satisfied=all_prereqs_satisfied
            )
        )
        step_num += 1

    return learning_path

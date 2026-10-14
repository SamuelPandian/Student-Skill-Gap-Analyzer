import pytest
from app.graph.prerequisites import (
    PrerequisiteEdge,
    generate_ordered_learning_path,
    detect_prerequisite_cycles,
    build_prerequisite_graph
)

def test_prerequisite_topological_ordering():
    # Python (1) -> Django (3) -> REST API (4) -> Docker (6)
    edges = [
        PrerequisiteEdge(skill_id=3, prerequisite_skill_id=1), # Django requires Python
        PrerequisiteEdge(skill_id=4, prerequisite_skill_id=3), # REST API requires Django
        PrerequisiteEdge(skill_id=6, prerequisite_skill_id=4), # Docker requires REST API
    ]
    
    skill_names = {1: "Python", 3: "Django", 4: "REST API", 6: "Docker"}
    # Gaps: Django (2/4), REST API (2/3), Docker (0/2)
    gaps = {
        3: (2.0, 4.0),
        4: (2.0, 3.0),
        6: (0.0, 2.0)
    }
    # Student satisfied Python (4/5)
    student_satisfied = {1}

    path = generate_ordered_learning_path(edges, skill_names, gaps, student_satisfied)

    assert len(path) == 3
    # Step 1 must be Django because Python is satisfied
    assert path[0].skill_name == "Django"
    assert path[0].status == "RECOMMENDED"
    assert path[0].prerequisites_satisfied is True

    # Step 2: REST API
    assert path[1].skill_name == "REST API"

    # Step 3: Docker
    assert path[2].skill_name == "Docker"

def test_prerequisite_cycle_detection():
    # Cycle: Skill A -> Skill B -> Skill A
    edges = [
        PrerequisiteEdge(skill_id=2, prerequisite_skill_id=1),
        PrerequisiteEdge(skill_id=1, prerequisite_skill_id=2)
    ]
    G = build_prerequisite_graph(edges)
    cycles = detect_prerequisite_cycles(G)
    assert len(cycles) > 0

# routers/visualize.py
from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .. import crud, dependencies
from typing import Optional, List, Dict, Set, Tuple

router = APIRouter(prefix="/graph", tags=["visualization"])
templates = Jinja2Templates(directory="templates")


def detect_cycles(edges: List[Dict]) -> Set[Tuple[str, str]]:
    """Detect all edges that are part of a cycle using DFS"""
    graph = {}
    for edge in edges:
        graph.setdefault(edge["from"], []).append(edge["to"])

    visited = set()
    rec_stack = set()
    cycle_edges = set()

    def dfs(node, parent=""):
        visited.add(node)
        rec_stack.add(node)

        if node in graph:
            for neighbor in graph[node]:
                if neighbor not in visited:
                    if dfs(neighbor, node):
                        cycle_edges.add((node, neighbor))
                        return True
                elif neighbor in rec_stack and neighbor != parent:
                    cycle_edges.add((node, neighbor))
                    return True

        rec_stack.remove(node)
        return False

    for node in list(graph.keys()):
        if node not in visited:
            dfs(node)

    return cycle_edges


@router.get("/visualize", response_class=HTMLResponse)
async def visualize_graph(
    request: Request,
    entity_type: Optional[str] = Query(None, description="legal or natural"),
    entity_id: Optional[int] = Query(None, description="Entity ID to explore"),
    depth: int = Query(3, ge=1, le=10, description="Traversal depth"),
    db: Session = Depends(dependencies.get_db)
):
    nodes = []
    edges = []
    cycle_edges = set()

    if not entity_type or not entity_id:
        return templates.TemplateResponse("graph.html", {
            "request": request,
            "nodes": [],
            "edges": [],
            "has_cycles": False,
            "center_entity": None
        })

    root_key = f"{entity_type}:{entity_id}"

    # Root node (highlighted)
    nodes.append({
        "id": root_key,
        "label": f"ROOT\n{entity_type.upper()} {entity_id}",
        "color": {"background": "#FF6B6B", "border": "#C21807", "highlight": {"background": "#FF4444"}},
        "shape": "box",
        "size": 40,
        "font": {"size": 16, "color": "white", "face": "bold"}
    })

    # Get downstream ownership
    downstream = crud.get_downstream_ownership(db, entity_type, entity_id, max_depth=depth)
    visited = {root_key}

    for row in downstream:
        from_key = f"{row['from_type']}:{row['from_id']}"
        to_key = f"{row['to_type']}:{row['to_id']}"

        # Add nodes
        for key, typ in [(from_key, row['from_type']), (to_key, row['to_type'])]:
            if key not in visited:
                nodes.append({
                    "id": key,
                    "label": f"{'Person' if typ=='natural' else 'Company'}\n{key.split(':')[1]}",
                    "color": "#90EE90" if typ == "natural" else "#87CEFA",
                    "shape": "dot",
                    "size": 28,
                    "font": {"size": 14}
                })
                visited.add(key)

        # Normal edge
        edge = {
            "from": from_key,
            "to": to_key,
            "label": f"{row['relation']}\n{row['share_percentage'] or '?'}%".strip(),
            "arrows": "to",
            "width": max(1.5, (row['share_percentage'] or 10) / 12),
            "color": {"color": "#2B7CE9", "highlight": "#2B7CE9"}
        }
        edges.append(edge)

    # Add UBOs (only for legal entities)
    if entity_type == "legal":
        ubos = crud.get_ultimate_beneficial_owners(db, entity_type, entity_id, min_shareholding=10.0)
        for ubo in ubos:
            person_key = f"natural:{ubo['person_id']}"
            if person_key not in visited:
                nodes.append({
                    "id": person_key,
                    "label": f"UBO {ubo['person_id']}\n{ubo['effective_shareholding']}%",
                    "color": {"background": "#FF0000", "border": "#AA0000"},
                    "shape": "box",
                    "size": 35,
                    "font": {"color": "white"}
                })
                visited.add(person_key)

            edges.append({
                "from": person_key,
                "to": root_key,
                "label": f"UBO {ubo['effective_shareholding']}%",
                "arrows": "to",
                "dashes": True,
                "color": {"color": "#FF0000", "highlight": "#FF0000"},
                "width": 5
            })

    # CYCLE DETECTION
    cycle_edges = detect_cycles(edges)

    # Apply cycle styling
    final_edges = []
    for edge in edges:
        edge_key = (edge["from"], edge["to"])
        if edge_key in cycle_edges:
            edge.update({
                "color": {"color": "#FF0000", "highlight": "#FF0000", "hover": "#FF0000"},
                "dashes": [5, 5],
                "width": 6,
                "shadow": True,
                "font": {"color": "#FF0000", "strokeWidth": 6, "strokeColor": "#000000"}
            })
        final_edges.append(edge)

    return templates.TemplateResponse("graph.html", {
        "request": request,
        "nodes": nodes,
        "edges": final_edges,
        "has_cycles": len(cycle_edges) > 0,
        "cycle_count": len(cycle_edges),
        "center_entity": root_key
    })
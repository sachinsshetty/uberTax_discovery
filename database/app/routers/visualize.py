# routers/visualize.py
from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from .. import crud, dependencies
from typing import Optional, List, Dict, Set, Tuple

router = APIRouter(prefix="/graph", tags=["visualization"])
templates = Jinja2Templates(directory="templates")


def search_entities(db: Session, query: str):
    query = query.strip().lower()
    q_pattern = f"%{query}%"
    q_num = query if query.isdigit() else "-1"

    natural = db.execute(text("""
        SELECT 'natural' as type, id, first_name || ' ' || last_name as name, tax_id
        FROM natural_persons
        WHERE lower(first_name || ' ' || last_name) LIKE :q
           OR tax_id ILIKE :q OR id::text = :q_num
    """), {"q": q_pattern, "q_num": q_num}).fetchall()

    legal = db.execute(text("""
        SELECT 'legal' as type, id, name, registration_number
        FROM legal_persons
        WHERE lower(name) LIKE :q
           OR registration_number ILIKE :q OR id::text = :q_num
    """), {"q": q_pattern, "q_num": q_num}).fetchall()

    results = []
    for row in natural + legal:
        label = row.name or row.registration_number or row.tax_id or f"ID {row.id}"
        results.append({
            "type": row.type,
            "id": row.id,
            "label": f"{label} ({row.type})",
            "key": f"{row.type}:{row.id}"
        })
    return results


def detect_and_mark_cycles(edges: List[Dict]):
    """Detect cycles and mark them with red dashed style"""
    graph = {}
    for e in edges:
        graph.setdefault(e["from"], []).append(e["to"])

    visited = set()
    rec_stack = set()
    cycle_edges = set()

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    cycle_edges.add((node, neighbor))
                    return True
            elif neighbor in rec_stack:
                cycle_edges.add((node, neighbor))
                return True
        rec_stack.remove(node)
        return False

    for node in list(graph.keys()):
        if node not in visited:
            dfs(node)

    # Apply red dashed style to cycle edges
    for e in edges:
        if (e["from"], e["to"]) in cycle_edges:
            e.update({
                "color": {"color": "#FF0000", "highlight": "#FF0000", "hover": "#FF0000"},
                "dashes": [10, 5],
                "width": 7,
                "font": {"color": "#FF0000", "size": 16, "strokeWidth": 5, "strokeColor": "#000"},
                "shadow": True
            })
    return len(cycle_edges) > 0


@router.get("/visualize", response_class=HTMLResponse)
async def visualize_graph(
    request: Request,
    search: Optional[str] = Query(None),
    min_share: Optional[float] = Query(None, ge=0, le=100),
    relation: Optional[str] = Query(None),
    entity_type_filter: Optional[str] = Query(None, alias="entity_type"),
    start_type: Optional[str] = Query(None),
    start_id: Optional[int] = Query(None),
    depth: int = Query(3, ge=1, le=8),
    db: Session = Depends(dependencies.get_db)
):
    nodes = []
    edges = []
    search_results = []
    has_cycles = False

    # Search
    if search:
        search_results = search_entities(db, search)
        if len(search_results) == 1 and not start_type:
            start_type = search_results[0]["type"]
            start_id = search_results[0]["id"]

    # Build graph
    if start_type and start_id:
        root_key = f"{start_type}:{start_id}"

        # Root node
        nodes.append({
            "id": root_key,
            "label": f"ROOT\n{start_type.upper()} {start_id}",
            "color": {"background": "#FF4444", "border": "#CC0000"},
            "shape": "box",
            "size": 48,
            "font": {"size": 18, "color": "white", "bold": True}
        })

        # Get connections
        connections = crud.get_connections_for_entity(db, start_type, start_id)
        if min_share:
            connections = [c for c in connections if c.share_percentage and c.share_percentage >= min_share]
        if relation:
            connections = [c for c in connections if c.relation.lower() == relation.lower()]

        visited = {root_key}

        for conn in connections:
            if entity_type_filter and conn.to_type != entity_type_filter:
                continue

            to_key = f"{conn.to_type}:{conn.to_id}"
            if to_key not in visited:
                nodes.append({
                    "id": to_key,
                    "label": f"{conn.to_type.upper()}\n{conn.to_id}",
                    "color": "#90EE90" if conn.to_type == "natural" else "#87CEFA",
                    "shape": "dot",
                    "size": 32
                })
                visited.add(to_key)

            edges.append({
                "from": root_key,
                "to": to_key,
                "label": f"{conn.relation}\n{conn.share_percentage or '?'}%",
                "arrows": "to",
                "width": max(2, (conn.share_percentage or 10) / 10),
                "color": {"color": "#2B7CE9"}
            })

        # UBOs
        if start_type == "legal":
            ubos = crud.get_ultimate_beneficial_owners(db, start_type, start_id, min_shareholding=min_share or 10)
            for ubo in ubos:
                key = f"natural:{ubo['person_id']}"
                if key not in visited:
                    nodes.append({
                        "id": key,
                        "label": f"UBO {ubo['person_id']}\n{ubo['effective_shareholding']}%",
                        "color": "#FF0000",
                        "shape": "box",
                        "size": 40
                    })
                    visited.add(key)
                edges.append({
                    "from": key,
                    "to": root_key,
                    "label": f"UBO {ubo['effective_shareholding']}%",
                    "dashes": True,
                    "color": "#FF0000",
                    "width": 6
                })

        # CYCLE DETECTION
        has_cycles = detect_and_mark_cycles(edges)

    return templates.TemplateResponse("graph.html", {
        "request": request,
        "nodes": nodes,
        "edges": edges,
        "search_results": search_results,
        "current_search": search,
        "filters": {"min_share": min_share, "relation": relation, "entity_type": entity_type_filter},
        "center_entity": f"{start_type}:{start_id}" if start_type and start_id else None,
        "has_cycles": has_cycles
    })
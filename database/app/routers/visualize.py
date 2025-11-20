# routers/visualize.py
from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .. import crud, dependencies
from typing import Optional

router = APIRouter(prefix="/graph", tags=["visualization"])

templates = Jinja2Templates(directory="templates")


@router.get("/visualize", response_class=HTMLResponse)
async def visualize_graph(
    request: Request,
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    depth: int = Query(3, ge=1, le=10),
    db: Session = Depends(dependencies.get_db)
):
    nodes = []
    edges = []

    if entity_type and entity_id:
        # Start from a specific entity and expand downstream/upstream
        downstream = crud.get_downstream_ownership(db, entity_type, entity_id, max_depth=depth)
        visited = set()

        # Add root node
        root_key = f"{entity_type}:{entity_id}"
        nodes.append({
            "id": root_key,
            "label": f"{'Company' if entity_type == 'legal' else 'Person'} {entity_id}",
            "color": "#90EE90" if entity_type == "natural" else "#87CEFA",
            "shape": "dot",
            "size": 30
        })
        visited.add(root_key)

        for row in downstream:
            from_key = f"{row['from_type']}:{row['from_id']}"
            to_key = f"{row['to_type']}:{row['to_id']}"

            if from_key not in visited:
                nodes.append({
                    "id": from_key,
                    "label": f"{'P' if row['from_type']=='natural' else 'C'}{row['from_id']}",
                    "color": "#90EE90" if row['from_type'] == "natural" else "#87CEFA",
                    "shape": "dot",
                    "size": 25
                })
                visited.add(from_key)

            if to_key not in visited:
                nodes.append({
                    "id": to_key,
                    "label": f"{'P' if row['to_type']=='natural' else 'C'}{row['to_id']}",
                    "color": "#90EE90" if row['to_type'] == "natural" else "#87CEFA",
                    "shape": "dot",
                    "size": 25
                })
                visited.add(to_key)

            edges.append({
                "from": from_key,
                "to": to_key,
                "label": f"{row['relation']} {row['share_percentage'] or ''}%".strip(),
                "arrows": "to",
                "color": {"color": "#2B7CE9" if row['share_percentage'] and row['share_percentage'] > 50 else "#848484"},
                "width": (row['share_percentage'] or 10) / 10
            })

        # Add UBOs if target is a company
        if entity_type == "legal":
            ubos = crud.get_ultimate_beneficial_owners(db, entity_type, entity_id, min_shareholding=10)
            for ubo in ubos:
                person_key = f"natural:{ubo['person_id']}"
                if person_key not in visited:
                    nodes.append({
                        "id": person_key,
                        "label": f"UBO {ubo['person_id']}\n{ubo['effective_shareholding']}%",
                        "color": "#FF6B6B",
                        "shape": "box",
                        "size": 35
                    })
                edges.append({
                    "from": person_key,
                    "to": root_key,
                    "label": f"UBO {ubo['effective_shareholding']}%",
                    "arrows": "to",
                    "color": {"color": "#FF0000", "highlight": "#FF0000"},
                    "dashes": True,
                    "width": 3
                })

    return templates.TemplateResponse(
        "graph.html",
        {
            "request": request,
            "nodes": nodes,
            "edges": edges,
            "center_entity": f"{entity_type}:{entity_id}" if entity_type and entity_id else None
        }
    )
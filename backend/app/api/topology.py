from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from backend.app.db.postgres import get_db
from backend.app.models.schemas import NodeCreate, EdgeCreate
from backend.app.engine.graph_rca import rca_engine

router = APIRouter(prefix="/topology", tags=["Infrastructure Topology Graph"])

@router.get("/")
def get_topology():
    """Retrieves full infrastructure dependency graph (nodes and edges)."""
    nodes = []
    for n, attrs in rca_engine.graph.nodes(data=True):
        nodes.append({"id": n, **attrs})
        
    edges = []
    for u, v, attrs in rca_engine.graph.edges(data=True):
        edges.append({"source": u, "target": v, "relation": attrs.get("relation", "DEPENDS_ON")})
        
    return {"nodes": nodes, "edges": edges}

@router.post("/node", status_code=status.HTTP_201_CREATED)
def add_topology_node(node: NodeCreate):
    """Adds a new host, microservice, container, or database node to the graph."""
    rca_engine.add_node(node.id, node.name, node.node_type, node.meta_info)
    return {"message": f"Topology node '{node.id}' added successfully."}

@router.post("/edge", status_code=status.HTTP_201_CREATED)
def add_topology_edge(edge: EdgeCreate):
    """Creates a directed dependency edge between two nodes in the graph."""
    rca_engine.add_edge(edge.source_id, edge.target_id, edge.relation)
    return {"message": f"Dependency edge '{edge.source_id}' -> '{edge.target_id}' created."}

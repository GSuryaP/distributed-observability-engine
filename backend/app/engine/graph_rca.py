import networkx as nx
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger("graph_rca_engine")

class ServiceDependencyGraphRCA:
    """
    Service Dependency Graph & Temporal RCA Engine using NetworkX.
    Models directed dependencies (e.g. Gateway -> Payment Service -> Postgres -> Host).
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        self._bootstrap_default_topology()

    def _bootstrap_default_topology(self):
        """Constructs sample multi-tier infrastructure dependency graph."""
        nodes = [
            ("api-gateway", {"name": "API Gateway", "type": "SERVICE"}),
            ("payment-service", {"name": "Payment Microservice", "type": "SERVICE"}),
            ("order-service", {"name": "Order Microservice", "type": "SERVICE"}),
            ("redis-cache", {"name": "Redis Session Cache", "type": "CACHE"}),
            ("postgres-db", {"name": "PostgreSQL Main DB", "type": "DATABASE"}),
            ("host-prod-01", {"name": "Production Host Node 01", "type": "HOST"}),
        ]
        
        edges = [
            ("api-gateway", "payment-service", "CALLS"),
            ("api-gateway", "order-service", "CALLS"),
            ("payment-service", "redis-cache", "DEPENDS_ON"),
            ("payment-service", "postgres-db", "DEPENDS_ON"),
            ("order-service", "postgres-db", "DEPENDS_ON"),
            ("postgres-db", "host-prod-01", "RUNS_ON"),
            ("redis-cache", "host-prod-01", "RUNS_ON"),
            ("payment-service", "host-prod-01", "RUNS_ON"),
        ]
        
        for n_id, attrs in nodes:
            self.graph.add_node(n_id, **attrs)
            
        for src, tgt, rel in edges:
            self.graph.add_edge(src, tgt, relation=rel)
            
        logger.info("Service Dependency Graph initialized with default microservice topology.")

    def add_node(self, node_id: str, name: str, node_type: str, meta: Dict[str, Any] = None):
        self.graph.add_node(node_id, name=name, type=node_type, meta=meta or {})

    def add_edge(self, source_id: str, target_id: str, relation: str = "DEPENDS_ON"):
        self.graph.add_edge(source_id, target_id, relation=relation)

    def analyze_root_cause(self, symptom_node_id: str, alert_nodes: List[str]) -> Tuple[str, float, List[str]]:
        """
        Traverses downstream dependencies from symptom node to find the primary candidate root cause.
        Returns: (suspected_root_cause_node_id, confidence_score, causal_path)
        """
        if symptom_node_id not in self.graph:
            logger.warning(f"Symptom node {symptom_node_id} not found in dependency graph.")
            return symptom_node_id, 0.5, [symptom_node_id]

        # Find all reachable nodes in dependency graph from symptom node
        descendants = list(nx.descendants(self.graph, symptom_node_id))
        candidate_nodes = [symptom_node_id] + descendants
        
        best_candidate = symptom_node_id
        max_score = 0.0
        best_path = [symptom_node_id]
        
        for candidate in candidate_nodes:
            try:
                path = nx.shortest_path(self.graph, source=symptom_node_id, target=candidate)
            except nx.NetworkXNoPath:
                path = [symptom_node_id, candidate]
                
            depth = len(path) - 1
            # Base score increases with distance from symptom towards leaf dependency
            is_anomalous_alert = candidate in alert_nodes
            score = 0.5 + (0.15 * depth) + (0.3 if is_anomalous_alert else 0.0)
            score = min(score, 0.98)
            
            if score > max_score:
                max_score = score
                best_candidate = candidate
                best_path = path
                
        return best_candidate, round(max_score, 2), best_path

rca_engine = ServiceDependencyGraphRCA()

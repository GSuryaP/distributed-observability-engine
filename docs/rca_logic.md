# Root Cause Analysis (RCA) Engine & Graph Traversal Logic

## 1. Graph Topology Representation

Infrastructure dependencies are modeled as a Directed Graph $G = (V, E)$:

* **Nodes ($V$)**:
  * `HOST`: Bare metal or VM compute nodes.
  * `CONTAINER`: Docker/Kubernetes container instances.
  * `SERVICE`: Microservice application endpoints.
  * `DATABASE`: PostgreSQL/MongoDB datastores.
  * `CACHE`: Redis/Memcached instances.

* **Edges ($E$)**:
  * `DEPENDS_ON`: Functional call or query dependency.
  * `RUNS_ON`: Hosting relationship.
  * `CALLS`: Direct synchronous HTTP/gRPC invocation.

---

## 2. Graph Traversal Algorithm

```text
[ Symptom Alert Triggered ]
           │
           ▼
[ Identify Symptom Node in Graph ]
           │
           ▼
[ Find All Downstream Reachable Nodes (nx.descendants) ]
           │
           ▼
[ For Each Candidate Node: ]
  ├── Compute Shortest Dependency Path
  ├── Check Active Alerts on Candidate Node
  └── Calculate Causal Confidence Score
           │
           ▼
[ Rank Candidate Nodes by Confidence Score ]
           │
           ▼
[ Select Top Candidate as Suspected Root Cause ]
           │
           ▼
[ Format Context Payload & Trigger LLM Post-Mortem Generator ]
```

---

## 3. Incident Deduplication Strategy

To prevent alert storms (e.g. 50 separate alerts for 1 root cause outage):
1. Alerts occurring within a 3-minute sliding window on topologically connected nodes are grouped under a single `IncidentID`.
2. Severity is assigned based on the maximum severity among grouped alerts (`CRITICAL > HIGH > WARNING > INFO`).
3. Re-evaluating RCA recalculates candidate scores without creating duplicate incident tickets.

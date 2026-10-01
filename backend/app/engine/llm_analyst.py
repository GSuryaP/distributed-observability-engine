import requests
import json
import logging
from typing import Dict, Any, List
from backend.app.config import settings

logger = logging.getLogger("llm_analyst")

class LLMIncidentAnalyst:
    """Converts structured RCA JSON data into human-readable incident explanations."""
    
    def generate_incident_report(
        self,
        incident_id: int,
        title: str,
        service_name: str,
        suspected_root_cause: str,
        confidence_score: float,
        causal_path: List[str],
        alerts: List[Dict[str, Any]]
    ) -> str:
        """Generates executive markdown incident post-mortem."""
        
        prompt_payload = {
            "incident_id": incident_id,
            "title": title,
            "affected_service": service_name,
            "suspected_root_cause": suspected_root_cause,
            "confidence_score": confidence_score,
            "causal_dependency_chain": " -> ".join(causal_path),
            "correlated_alerts": [a.get("message") for a in alerts]
        }

        # Try LLM API (OpenAI or Ollama) if configured
        if settings.OPENAI_API_KEY:
            try:
                headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}
                body = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a Senior Site Reliability Engineer (SRE). Write a concise, actionable incident post-mortem report in Markdown."},
                        {"role": "user", "content": f"Analyze this incident: {json.dumps(prompt_payload)}"}
                    ],
                    "temperature": 0.2
                }
                resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=8)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"OpenAI API call failed ({e}). Falling back to deterministic analyst template.")

        # Fallback deterministic markdown post-mortem template
        return self._generate_fallback_template(prompt_payload)

    def _generate_fallback_template(self, data: Dict[str, Any]) -> str:
        alerts_list = "\n".join([f"- {a}" for a in data["correlated_alerts"]]) or "- No correlated metric alerts."
        return f"""### 🚨 Incident Post-Mortem Report #{data['incident_id']}

**Title:** {data['title']}  
**Affected Service:** `{data['affected_service']}`  
**Suspected Root Cause:** `{data['suspected_root_cause']}` (Confidence: {int(data['confidence_score'] * 100)}%)  

#### 🔍 Causal Propagation Chain
```text
{data['causal_dependency_chain']}
```

#### ⚡ Symptoms & Correlated Alerts
{alerts_list}

#### 🛠️ Recommended Remediation Steps
1. Inspect container logs and CPU/RAM saturation on `{data['suspected_root_cause']}`.
2. Check database connection pool and lock wait times if latency spiked.
3. Restart degraded worker pod/service if metric slope remains positive.
4. Scale replica count if HTTP request rate exceeds baseline.
"""

llm_analyst = LLMIncidentAnalyst()

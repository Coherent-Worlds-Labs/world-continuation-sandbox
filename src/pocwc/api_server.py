from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .metrics import RuntimeStats, compute_metrics
from .orchestrator import SimulationConfig, SimulationEngine


class WorldAPIHandler(BaseHTTPRequestHandler):
    store = None
    static_root = Path(__file__).parent / "web" / "ui"

    def _json(self, payload: dict | list, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_static(self, filename: str) -> None:
        path = self.static_root / filename
        if not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = path.read_bytes()
        ctype = "text/plain"
        if filename.endswith(".html"):
            ctype = "text/html; charset=utf-8"
        elif filename.endswith(".js"):
            ctype = "application/javascript; charset=utf-8"
        elif filename.endswith(".css"):
            ctype = "text/css; charset=utf-8"

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._serve_static("index.html")
            return
        if path in ("/app.js", "/styles.css"):
            self._serve_static(path.lstrip("/"))
            return

        if path == "/api/health":
            self._json({"status": "ok"})
            return

        if path == "/api/overview":
            branches = self.store.list_branches()
            results = self.store.list_verification_results()
            metrics = compute_metrics(branches, results, RuntimeStats())
            self._json({"branches": branches, "metrics": metrics, "controller": self.store.latest_epoch()})
            return

        if path == "/api/branches":
            self._json(self.store.list_branches())
            return

        if path.startswith("/api/states/"):
            state_id = path.split("/", 3)[-1]
            state = self.store.get_state(state_id)
            if not state:
                self._json({"error": "state not found"}, 404)
                return
            self._json(state)
            return

        if path == "/api/states":
            qs = parse_qs(parsed.query)
            branch_id = qs.get("branch_id", [None])[0]
            self._json(self.store.list_states(branch_id=branch_id))
            return

        if path.startswith("/api/challenges/"):
            challenge_id = path.split("/", 3)[-1]
            challenge = self.store.get_challenge(challenge_id)
            if not challenge:
                self._json({"error": "challenge not found"}, 404)
                return
            candidates = self.store.list_candidates(challenge_id=challenge_id)
            self._json({"challenge": challenge, "candidates": candidates})
            return

        if path == "/api/challenges":
            self._json(self.store.list_challenges())
            return

        if path.startswith("/api/candidates/"):
            candidate_id = path.split("/", 3)[-1]
            candidate = self.store.get_candidate(candidate_id)
            if not candidate:
                self._json({"error": "candidate not found"}, 404)
                return
            verification = self.store.list_verification_results(candidate_id=candidate_id)
            self._json({"candidate": candidate, "verification": verification})
            return

        if path == "/api/metrics":
            branches = self.store.list_branches()
            verification = self.store.list_verification_results()
            self._json(compute_metrics(branches, verification, RuntimeStats()))
            return

        if path == "/api/search":
            qs = parse_qs(parsed.query)
            tag = (qs.get("tag", [""])[0] or "").lower().strip()
            matches = []
            for st in self.store.list_states():
                entities = [e.lower() for e in st.get("meta_m", {}).get("entities", [])]
                threads = [t.lower() for t in st.get("meta_m", {}).get("threads", [])]
                if tag and any(tag in value for value in entities + threads):
                    matches.append(st)
            self._json(matches)
            return

        if path == "/api/story":
            qs = parse_qs(parsed.query)
            branch_id = qs.get("branch_id", [None])[0]
            limit_raw = qs.get("limit", ["200"])[0]
            try:
                limit = int(limit_raw)
            except ValueError:
                limit = 200
            events = self.store.list_story_events(branch_id=branch_id, limit=limit)
            self._json(events)
            return

        if path == "/api/story/summary":
            qs = parse_qs(parsed.query)
            branch_id = qs.get("branch_id", ["branch-main"])[0]
            memory = self.store.get_story_memory(branch_id)
            if not memory:
                self._json({"error": "story summary not found"}, 404)
                return
            self._json(memory)
            return

        if path == "/api/facts/active":
            qs = parse_qs(parsed.query)
            branch_id = qs.get("branch_id", ["branch-main"])[0]
            limit_raw = qs.get("limit", ["200"])[0]
            try:
                limit = int(limit_raw)
            except ValueError:
                limit = 200
            self._json(self.store.list_active_facts(branch_id, limit=limit))
            return

        if path == "/api/progress/diagnostics":
            qs = parse_qs(parsed.query)
            branch_id = qs.get("branch_id", ["branch-main"])[0]
            limit_raw = qs.get("limit", ["30"])[0]
            try:
                limit = int(limit_raw)
            except ValueError:
                limit = 30
            challenges = self.store.list_challenges(branch_id=branch_id)[-max(1, min(limit, 200)) :]
            challenge_ids = {str(ch.get("challenge_id", "")) for ch in challenges}
            candidates = [
                c
                for c in self.store.list_candidates()
                if str(c.get("challenge_id", "")) in challenge_ids
            ]
            by_candidate = {str(c.get("candidate_id", "")): [] for c in candidates}
            for row in self.store.list_verification_results():
                cid = str(row.get("candidate_id", ""))
                if cid in by_candidate:
                    by_candidate[cid].append(row)
            payload = []
            for cand in candidates:
                cid = str(cand.get("candidate_id", ""))
                meta = cand.get("meta_m", {})
                payload.append(
                    {
                        "challenge_id": cand.get("challenge_id"),
                        "candidate_id": cid,
                        "prover_id": cand.get("prover_id"),
                        "status": cand.get("status"),
                        "fact_object": meta.get("fact_object", {}),
                        "what_changed_since_previous_step": meta.get("what_changed_since_previous_step", ""),
                        "verification": by_candidate.get(cid, []),
                    }
                )
            self._json(payload)
            return

        self.send_error(HTTPStatus.NOT_FOUND)


def run_api_server(
    db_path: Path,
    host: str = "127.0.0.1",
    port: int = 8080,
    world_config_path: Path = Path("config/world.default.json"),
) -> None:
    engine = SimulationEngine(SimulationConfig(db_path=db_path, world_config_path=world_config_path))
    engine._seed_genesis()
    WorldAPIHandler.store = engine.store
    server = ThreadingHTTPServer((host, port), WorldAPIHandler)
    print(f"Serving PoCWC world browser at http://{host}:{port}")
    server.serve_forever()

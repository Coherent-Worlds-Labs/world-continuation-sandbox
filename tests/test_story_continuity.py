from __future__ import annotations

import json
import threading
import time
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen

from pocwc.api_server import WorldAPIHandler
from pocwc.orchestrator import SimulationConfig, SimulationEngine


class StoryContinuityTests(unittest.TestCase):
    def test_story_memory_and_events_populate(self) -> None:
        db = Path("data/test_story_memory.db")
        if db.exists():
            db.unlink()

        engine = SimulationEngine(SimulationConfig(db_path=db, steps=6, seed=17))
        engine.run(6)

        memory = engine.store.get_story_memory("branch-main")
        events = engine.store.list_story_events(branch_id="branch-main", limit=100)

        self.assertIsNotNone(memory)
        self.assertIn("summary", memory)
        self.assertGreaterEqual(len(events), 1)
        self.assertIn("scene", events[0])

    def test_story_api_endpoints(self) -> None:
        db = Path("data/test_story_api.db")
        if db.exists():
            db.unlink()

        engine = SimulationEngine(SimulationConfig(db_path=db, steps=4, seed=9))
        engine.run(4)

        WorldAPIHandler.store = engine.store
        server = ThreadingHTTPServer(("127.0.0.1", 8093), WorldAPIHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        time.sleep(0.2)
        try:
            summary = json.loads(urlopen("http://127.0.0.1:8093/api/story/summary?branch_id=branch-main").read().decode("utf-8"))
            timeline = json.loads(urlopen("http://127.0.0.1:8093/api/story?branch_id=branch-main&limit=20").read().decode("utf-8"))
            self.assertIn("summary", summary)
            self.assertGreaterEqual(len(timeline), 1)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()

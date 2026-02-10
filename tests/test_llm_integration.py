from __future__ import annotations

import os
import unittest
from pathlib import Path

from pocwc.llm import LLMSettings, create_llm_adapter
from pocwc.orchestrator import SimulationConfig, SimulationEngine


class LLMSettingsTests(unittest.TestCase):
    def test_openrouter_settings_disabled_without_key(self) -> None:
        old = dict(os.environ)
        try:
            os.environ["POCWC_LLM_PROVIDER"] = "openrouter"
            os.environ["OPENROUTER_MODEL"] = "openai/gpt-4o-mini"
            os.environ.pop("OPENROUTER_API_KEY", None)
            settings = LLMSettings.from_env()
            self.assertEqual(settings.provider, "openrouter")
            self.assertFalse(settings.enabled)
            self.assertIsNone(create_llm_adapter(settings))
        finally:
            os.environ.clear()
            os.environ.update(old)

    def test_openrouter_settings_enabled_with_key(self) -> None:
        old = dict(os.environ)
        try:
            os.environ["POCWC_LLM_PROVIDER"] = "openrouter"
            os.environ["OPENROUTER_MODEL"] = "openai/gpt-4o-mini"
            os.environ["OPENROUTER_API_KEY"] = "test-key"
            settings = LLMSettings.from_env()
            self.assertTrue(settings.enabled)
            self.assertIsNotNone(create_llm_adapter(settings))
        finally:
            os.environ.clear()
            os.environ.update(old)


class FallbackExecutionTests(unittest.TestCase):
    def test_simulation_runs_without_llm_key(self) -> None:
        db = Path("data/test_world_llm_fallback.db")
        if db.exists():
            db.unlink()

        old = dict(os.environ)
        try:
            os.environ["POCWC_LLM_PROVIDER"] = "openrouter"
            os.environ["OPENROUTER_MODEL"] = "openai/gpt-4o-mini"
            os.environ.pop("OPENROUTER_API_KEY", None)
            engine = SimulationEngine(
                SimulationConfig(db_path=db, steps=5, seed=19, llm_provider="openrouter", llm_model="openai/gpt-4o-mini")
            )
            summary = engine.run(5)
            self.assertGreaterEqual(summary["attempted_challenges"], 5)
        finally:
            os.environ.clear()
            os.environ.update(old)

    def test_story_language_metadata_propagates(self) -> None:
        db = Path("data/test_world_story_language.db")
        if db.exists():
            db.unlink()

        engine = SimulationEngine(
            SimulationConfig(
                db_path=db,
                steps=2,
                seed=23,
                story_language="spanish",
            )
        )
        engine.run(2)
        states = engine.store.list_states(branch_id="branch-main")
        latest = states[-1]
        self.assertEqual(latest["meta_m"].get("story_language_requested"), "spanish")


if __name__ == "__main__":
    unittest.main()

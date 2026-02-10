from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any


class WorldStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.isolation_level = None
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with closing(self._conn()) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS branches (
                    branch_id TEXT PRIMARY KEY,
                    head_state_id TEXT,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    semantic_debt_est REAL NOT NULL,
                    uncertainty REAL NOT NULL,
                    closure_pressure REAL NOT NULL,
                    chaos_pressure REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS states (
                    state_id TEXT PRIMARY KEY,
                    branch_id TEXT NOT NULL,
                    parent_state_id TEXT,
                    height INTEGER NOT NULL,
                    artifact_x TEXT NOT NULL,
                    meta_m TEXT NOT NULL,
                    challenge_ref TEXT,
                    acceptance_summary TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS challenges (
                    challenge_id TEXT PRIMARY KEY,
                    branch_id TEXT NOT NULL,
                    parent_state_id TEXT NOT NULL,
                    projection TEXT NOT NULL,
                    directive_type TEXT NOT NULL,
                    difficulty_params TEXT NOT NULL,
                    verifier_policy TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS candidates (
                    candidate_id TEXT PRIMARY KEY,
                    challenge_id TEXT NOT NULL,
                    prover_id TEXT NOT NULL,
                    artifact_x TEXT NOT NULL,
                    meta_m TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS verification_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id TEXT NOT NULL,
                    verifier_id TEXT NOT NULL,
                    level_max_reached TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    score REAL NOT NULL,
                    signals TEXT NOT NULL,
                    notes TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS controller_epochs (
                    step INTEGER PRIMARY KEY,
                    difficulty TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    theta REAL NOT NULL,
                    metrics TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS story_memory (
                    branch_id TEXT PRIMARY KEY,
                    summary TEXT NOT NULL,
                    continuity TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS story_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    branch_id TEXT NOT NULL,
                    state_id TEXT NOT NULL,
                    height INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    scene TEXT NOT NULL,
                    surface_confirmation TEXT NOT NULL,
                    alternative_compatibility TEXT NOT NULL,
                    social_effect TEXT NOT NULL,
                    deferred_tension TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS branch_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    branch_id TEXT NOT NULL,
                    state_id TEXT NOT NULL,
                    fact_id TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    predicate TEXT NOT NULL,
                    object TEXT NOT NULL,
                    time_hint TEXT NOT NULL,
                    location_hint TEXT NOT NULL,
                    evidence_type TEXT NOT NULL,
                    falsifiable INTEGER NOT NULL,
                    fact_text TEXT NOT NULL,
                    fact_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def upsert_branch(self, branch: dict[str, Any]) -> None:
        with closing(self._conn()) as conn:
            conn.execute(
                """
                INSERT INTO branches(branch_id, head_state_id, created_at, status, semantic_debt_est, uncertainty, closure_pressure, chaos_pressure)
                VALUES(:branch_id, :head_state_id, :created_at, :status, :semantic_debt_est, :uncertainty, :closure_pressure, :chaos_pressure)
                ON CONFLICT(branch_id) DO UPDATE SET
                  head_state_id=excluded.head_state_id,
                  status=excluded.status,
                  semantic_debt_est=excluded.semantic_debt_est,
                  uncertainty=excluded.uncertainty,
                  closure_pressure=excluded.closure_pressure,
                  chaos_pressure=excluded.chaos_pressure
                """,
                branch,
            )

    def insert_state(self, state: dict[str, Any]) -> None:
        payload = dict(state)
        payload["meta_m"] = json.dumps(payload["meta_m"], ensure_ascii=False)
        payload["acceptance_summary"] = json.dumps(payload["acceptance_summary"], ensure_ascii=False)
        with closing(self._conn()) as conn:
            conn.execute(
                """
                INSERT INTO states(state_id, branch_id, parent_state_id, height, artifact_x, meta_m, challenge_ref, acceptance_summary, created_at)
                VALUES(:state_id, :branch_id, :parent_state_id, :height, :artifact_x, :meta_m, :challenge_ref, :acceptance_summary, :created_at)
                """,
                payload,
            )

    def insert_challenge(self, challenge: dict[str, Any]) -> None:
        payload = dict(challenge)
        payload["difficulty_params"] = json.dumps(payload["difficulty_params"], ensure_ascii=False)
        payload["verifier_policy"] = json.dumps(payload["verifier_policy"], ensure_ascii=False)
        with closing(self._conn()) as conn:
            conn.execute(
                """
                INSERT INTO challenges(challenge_id, branch_id, parent_state_id, projection, directive_type, difficulty_params, verifier_policy, created_at)
                VALUES(:challenge_id, :branch_id, :parent_state_id, :projection, :directive_type, :difficulty_params, :verifier_policy, :created_at)
                """,
                payload,
            )

    def insert_candidate(self, candidate: dict[str, Any]) -> None:
        payload = dict(candidate)
        payload["meta_m"] = json.dumps(payload["meta_m"], ensure_ascii=False)
        with closing(self._conn()) as conn:
            conn.execute(
                """
                INSERT INTO candidates(candidate_id, challenge_id, prover_id, artifact_x, meta_m, status, created_at)
                VALUES(:candidate_id, :challenge_id, :prover_id, :artifact_x, :meta_m, :status, :created_at)
                """,
                payload,
            )

    def update_candidate_status(self, candidate_id: str, status: str) -> None:
        with closing(self._conn()) as conn:
            conn.execute("UPDATE candidates SET status=? WHERE candidate_id=?", (status, candidate_id))

    def insert_verification_result(self, result: dict[str, Any]) -> None:
        payload = dict(result)
        payload["signals"] = json.dumps(payload["signals"], ensure_ascii=False)
        with closing(self._conn()) as conn:
            conn.execute(
                """
                INSERT INTO verification_results(candidate_id, verifier_id, level_max_reached, verdict, score, signals, notes, created_at)
                VALUES(:candidate_id, :verifier_id, :level_max_reached, :verdict, :score, :signals, :notes, :created_at)
                """,
                payload,
            )

    def insert_controller_epoch(self, row: dict[str, Any]) -> None:
        payload = dict(row)
        payload["difficulty"] = json.dumps(payload["difficulty"], ensure_ascii=False)
        payload["metrics"] = json.dumps(payload["metrics"], ensure_ascii=False)
        with closing(self._conn()) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO controller_epochs(step, difficulty, mode, theta, metrics, created_at)
                VALUES(:step, :difficulty, :mode, :theta, :metrics, :created_at)
                """,
                payload,
            )

    def upsert_story_memory(self, row: dict[str, Any]) -> None:
        payload = dict(row)
        payload["continuity"] = json.dumps(payload["continuity"], ensure_ascii=False)
        with closing(self._conn()) as conn:
            conn.execute(
                """
                INSERT INTO story_memory(branch_id, summary, continuity, updated_at)
                VALUES(:branch_id, :summary, :continuity, :updated_at)
                ON CONFLICT(branch_id) DO UPDATE SET
                  summary=excluded.summary,
                  continuity=excluded.continuity,
                  updated_at=excluded.updated_at
                """,
                payload,
            )

    def get_story_memory(self, branch_id: str) -> dict[str, Any] | None:
        with closing(self._conn()) as conn:
            row = conn.execute("SELECT * FROM story_memory WHERE branch_id=?", (branch_id,)).fetchone()
        return self._decode_row(row, ("continuity",)) if row else None

    def insert_story_event(self, row: dict[str, Any]) -> None:
        payload = dict(row)
        alt = payload.get("alternative_compatibility", [])
        payload["alternative_compatibility"] = json.dumps(alt, ensure_ascii=False)
        with closing(self._conn()) as conn:
            conn.execute(
                """
                INSERT INTO story_events(branch_id, state_id, height, title, scene, surface_confirmation, alternative_compatibility, social_effect, deferred_tension, created_at)
                VALUES(:branch_id, :state_id, :height, :title, :scene, :surface_confirmation, :alternative_compatibility, :social_effect, :deferred_tension, :created_at)
                """,
                payload,
            )

    def list_story_events(self, branch_id: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        cap = max(1, min(limit, 1000))
        with closing(self._conn()) as conn:
            if branch_id:
                rows = conn.execute(
                    "SELECT * FROM story_events WHERE branch_id=? ORDER BY height ASC, id ASC LIMIT ?",
                    (branch_id, cap),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM story_events ORDER BY branch_id ASC, height ASC, id ASC LIMIT ?",
                    (cap,),
                ).fetchall()
        return [self._decode_row(r, ("alternative_compatibility",)) for r in rows]

    def insert_branch_fact(self, row: dict[str, Any]) -> None:
        with closing(self._conn()) as conn:
            conn.execute(
                """
                INSERT INTO branch_facts(
                    branch_id, state_id, fact_id, subject, predicate, object, time_hint, location_hint,
                    evidence_type, falsifiable, fact_text, fact_hash, created_at
                )
                VALUES(
                    :branch_id, :state_id, :fact_id, :subject, :predicate, :object, :time_hint, :location_hint,
                    :evidence_type, :falsifiable, :fact_text, :fact_hash, :created_at
                )
                """,
                row,
            )

    def list_branch_facts(self, branch_id: str, limit: int = 200) -> list[dict[str, Any]]:
        cap = max(1, min(limit, 5000))
        with closing(self._conn()) as conn:
            rows = conn.execute(
                "SELECT * FROM branch_facts WHERE branch_id=? ORDER BY id DESC LIMIT ?",
                (branch_id, cap),
            ).fetchall()
        return [dict(r) for r in rows]

    def _decode_row(self, row: sqlite3.Row, json_fields: tuple[str, ...]) -> dict[str, Any]:
        data = dict(row)
        for field in json_fields:
            if data.get(field):
                data[field] = json.loads(data[field])
        return data

    def list_branches(self) -> list[dict[str, Any]]:
        with closing(self._conn()) as conn:
            rows = conn.execute("SELECT * FROM branches ORDER BY created_at ASC").fetchall()
        return [dict(r) for r in rows]

    def get_branch(self, branch_id: str) -> dict[str, Any] | None:
        with closing(self._conn()) as conn:
            row = conn.execute("SELECT * FROM branches WHERE branch_id=?", (branch_id,)).fetchone()
        return dict(row) if row else None

    def list_states(self, branch_id: str | None = None) -> list[dict[str, Any]]:
        with closing(self._conn()) as conn:
            if branch_id:
                rows = conn.execute("SELECT * FROM states WHERE branch_id=? ORDER BY height ASC", (branch_id,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM states ORDER BY created_at ASC").fetchall()
        return [self._decode_row(r, ("meta_m", "acceptance_summary")) for r in rows]

    def get_state(self, state_id: str) -> dict[str, Any] | None:
        with closing(self._conn()) as conn:
            row = conn.execute("SELECT * FROM states WHERE state_id=?", (state_id,)).fetchone()
        return self._decode_row(row, ("meta_m", "acceptance_summary")) if row else None

    def list_challenges(self, branch_id: str | None = None) -> list[dict[str, Any]]:
        with closing(self._conn()) as conn:
            if branch_id:
                rows = conn.execute("SELECT * FROM challenges WHERE branch_id=? ORDER BY created_at ASC", (branch_id,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM challenges ORDER BY created_at ASC").fetchall()
        return [self._decode_row(r, ("difficulty_params", "verifier_policy")) for r in rows]

    def get_challenge(self, challenge_id: str) -> dict[str, Any] | None:
        with closing(self._conn()) as conn:
            row = conn.execute("SELECT * FROM challenges WHERE challenge_id=?", (challenge_id,)).fetchone()
        return self._decode_row(row, ("difficulty_params", "verifier_policy")) if row else None

    def list_candidates(self, challenge_id: str | None = None) -> list[dict[str, Any]]:
        with closing(self._conn()) as conn:
            if challenge_id:
                rows = conn.execute("SELECT * FROM candidates WHERE challenge_id=? ORDER BY created_at ASC", (challenge_id,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM candidates ORDER BY created_at ASC").fetchall()
        return [self._decode_row(r, ("meta_m",)) for r in rows]

    def get_candidate(self, candidate_id: str) -> dict[str, Any] | None:
        with closing(self._conn()) as conn:
            row = conn.execute("SELECT * FROM candidates WHERE candidate_id=?", (candidate_id,)).fetchone()
        return self._decode_row(row, ("meta_m",)) if row else None

    def list_verification_results(self, candidate_id: str | None = None) -> list[dict[str, Any]]:
        with closing(self._conn()) as conn:
            if candidate_id:
                rows = conn.execute(
                    "SELECT candidate_id, verifier_id, level_max_reached, verdict, score, signals, notes, created_at FROM verification_results WHERE candidate_id=? ORDER BY id ASC",
                    (candidate_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT candidate_id, verifier_id, level_max_reached, verdict, score, signals, notes, created_at FROM verification_results ORDER BY id ASC"
                ).fetchall()
        return [self._decode_row(r, ("signals",)) for r in rows]

    def latest_epoch(self) -> dict[str, Any] | None:
        with closing(self._conn()) as conn:
            row = conn.execute("SELECT * FROM controller_epochs ORDER BY step DESC LIMIT 1").fetchone()
        return self._decode_row(row, ("difficulty", "metrics")) if row else None


from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator, model_validator


ALLOWED_FACT_TYPES: tuple[str, ...] = (
    "public_artifact",
    "witness",
    "measurement",
    "institutional_action",
    "resource_change",
    "agent_commitment",
)


@dataclass(slots=True)
class FactSchemaResult:
    normalized: dict[str, Any]
    errors: list[dict[str, Any]]
    coercions: list[str]


class FactObjectModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    type: str
    content: str
    introduced_by: str
    time: str
    evidence: list[str]
    interpretation_affinity: dict[str, float]
    references: list[str]
    artifact_kind: str | None = None
    artifact_locator: str | None = None
    artifact_identifier: str | None = None

    @field_validator("id", "type", "content", "introduced_by", "time")
    @classmethod
    def _non_empty_text(cls, value: str) -> str:
        text = str(value).strip()
        if not text:
            raise ValueError("must be non-empty")
        return text

    @field_validator("evidence")
    @classmethod
    def _evidence_non_empty(cls, value: list[str]) -> list[str]:
        cleaned = [str(x).strip() for x in value if str(x).strip()]
        if not cleaned:
            raise ValueError("must contain at least one non-empty item")
        return cleaned

    @field_validator("references")
    @classmethod
    def _refs_normalized(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        for item in value:
            text = str(item).strip().upper()
            if text and text not in normalized:
                normalized.append(text)
        return normalized

    @field_validator("interpretation_affinity")
    @classmethod
    def _affinity_numeric(cls, value: dict[str, float]) -> dict[str, float]:
        if not value:
            raise ValueError("must be non-empty")
        normalized: dict[str, float] = {}
        for key, raw in value.items():
            k = str(key).strip()
            if not k:
                raise ValueError("contains empty interpretation key")
            try:
                fv = float(raw)
            except (TypeError, ValueError) as exc:
                raise ValueError("contains non-numeric value") from exc
            normalized[k] = fv
        return normalized

    @model_validator(mode="after")
    def _semantic_checks(self) -> "FactObjectModel":
        if self.type not in ALLOWED_FACT_TYPES:
            raise ValueError("type is outside allowed enum")
        total = sum(float(v) for v in self.interpretation_affinity.values())
        if abs(total - 1.0) > 0.08:
            raise ValueError("interpretation_affinity must sum to 1")
        for val in self.interpretation_affinity.values():
            if val < 0.0 or val > 1.0:
                raise ValueError("interpretation_affinity values must be in [0,1]")
        return self


def _default_affinity(policy: dict[str, Any]) -> dict[str, float]:
    raw = policy.get("coercion_default_affinity", {"I1": 0.34, "I2": 0.33, "I3": 0.33})
    if not isinstance(raw, dict):
        return {"I1": 0.34, "I2": 0.33, "I3": 0.33}
    cleaned: dict[str, float] = {}
    for key, value in raw.items():
        try:
            cleaned[str(key)] = float(value)
        except (TypeError, ValueError):
            continue
    total = sum(cleaned.values())
    if total <= 0.0:
        return {"I1": 0.34, "I2": 0.33, "I3": 0.33}
    return {k: round(v / total, 3) for k, v in cleaned.items()}


def _normalize_fact_type(raw: Any) -> str:
    text = str(raw or "").strip().lower()
    mapping = {
        "fact": "public_artifact",
        "new_fact": "public_artifact",
        "artifact": "public_artifact",
        "publicartifact": "public_artifact",
        "institution action": "institutional_action",
        "agent commitment": "agent_commitment",
        "resource change": "resource_change",
    }
    return mapping.get(text, text.replace(" ", "_"))


def _format_validation_errors(err: ValidationError) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for issue in err.errors():
        loc = ".".join(str(x) for x in issue.get("loc", []))
        details.append(
            {
                "path": loc,
                "msg": str(issue.get("msg", "")),
                "type": str(issue.get("type", "")),
                "got": issue.get("input"),
            }
        )
    return details


def validate_and_normalize_fact_object(
    raw_fact: Any,
    policy: dict[str, Any],
    *,
    expected_fact_type: str = "",
    allow_coercion: bool = False,
) -> FactSchemaResult:
    if not isinstance(raw_fact, dict):
        return FactSchemaResult(normalized={}, errors=[{"path": "fact_object", "msg": "must be object", "type": "type_error", "got": raw_fact}], coercions=[])

    obj = dict(raw_fact)
    coercions: list[str] = []

    obj["id"] = str(obj.get("id", "")).strip().upper()
    obj["type"] = _normalize_fact_type(obj.get("type", ""))
    refs = obj.get("references", [])
    if isinstance(refs, list):
        obj["references"] = [str(x).strip().upper() for x in refs if str(x).strip()]
    else:
        obj["references"] = []

    if allow_coercion and not isinstance(obj.get("interpretation_affinity"), dict):
        obj["interpretation_affinity"] = _default_affinity(policy)
        coercions.append("interpretation_affinity:coerced_to_default_map")

    # Public artifact strict fields.
    if obj.get("type") == "public_artifact":
        allowed_kinds = [str(x).strip() for x in policy.get("artifact_kind_enum", ["registry_record", "evidence_card", "bulletin", "report", "photo", "map"]) if str(x).strip()]
        if not str(obj.get("artifact_kind", "")).strip():
            if allow_coercion and allowed_kinds:
                obj["artifact_kind"] = allowed_kinds[0]
                coercions.append("artifact_kind:defaulted")
        if str(obj.get("artifact_kind", "")).strip() not in allowed_kinds and allow_coercion and allowed_kinds:
            obj["artifact_kind"] = allowed_kinds[0]
            coercions.append("artifact_kind:normalized_to_enum")

        if not str(obj.get("artifact_locator", "")).strip() and allow_coercion:
            obj["artifact_locator"] = "unspecified locator"
            coercions.append("artifact_locator:defaulted")

        ident = str(obj.get("artifact_identifier", "")).strip()
        pattern = str(policy.get("artifact_identifier_pattern", r"^[A-Z]+-\d{2,6}$"))
        if ident and not re.fullmatch(pattern, ident):
            if allow_coercion:
                digits = "".join(ch for ch in ident if ch.isdigit())
                obj["artifact_identifier"] = f"R-{digits[-3:]}" if digits else "R-000"
                coercions.append("artifact_identifier:normalized")
        elif not ident and allow_coercion:
            obj["artifact_identifier"] = "R-000"
            coercions.append("artifact_identifier:defaulted")

    # Directive contract expected type.
    if expected_fact_type and str(obj.get("type", "")).strip() and str(obj.get("type", "")).strip() != expected_fact_type and allow_coercion:
        obj["type"] = expected_fact_type
        coercions.append("type:coerced_to_expected_fact_type")

    try:
        parsed = FactObjectModel.model_validate(obj)
    except ValidationError as exc:
        return FactSchemaResult(normalized=obj, errors=_format_validation_errors(exc), coercions=coercions)

    normalized = parsed.model_dump()

    # Policy-level affinity key whitelist.
    allowed_affinity_keys = [str(x).strip() for x in policy.get("interpretation_keys", ["I1", "I2", "I3"]) if str(x).strip()]
    if allowed_affinity_keys:
        bad_keys = [k for k in normalized["interpretation_affinity"].keys() if k not in allowed_affinity_keys]
        if bad_keys:
            return FactSchemaResult(
                normalized=normalized,
                errors=[
                    {
                        "path": "interpretation_affinity",
                        "msg": f"contains unknown keys: {', '.join(bad_keys)}",
                        "type": "value_error.affinity_keys",
                        "got": dict(normalized["interpretation_affinity"]),
                    }
                ],
                coercions=coercions,
            )

    return FactSchemaResult(normalized=normalized, errors=[], coercions=coercions)


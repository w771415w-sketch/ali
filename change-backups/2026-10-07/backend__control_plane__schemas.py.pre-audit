from __future__
from dataclasses import dataclass, field, asdict
from typing import Any
import time, uuid


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

@dataclass
class Evidence:
    kind: str
    description: str
    value: Any = None
    source: str | None = None
    verified: bool = False
    created_at: float = field(default_factory=time.time)
    def to_dict(self): return asdict(self)

@dataclass
class Requirement:
    id: str
    text: str
    kind: str = "must"
    status: str = "proposed"
    source: str = "user"
    confidence: float = 0.0
    evidence: list[Evidence] = field(default_factory=list)
    conflicts_with: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    def to_dict(self): return asdict(self)

@dataclass
class AcceptanceCriterion:
    id: str
    text: str
    required: bool = True
    status: str = "pending"
    evidence: list[Evidence] = field(default_factory=list)
    def to_dict(self): return asdict(self)

@dataclass
class Decision:
    id: str
    topic: str
    choice: str
    reason: str
    status: str = "active"
    affected_components: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    def to_dict(self): return asdict(self)

@dataclass
class Task:
    id: str
    title: str
    status: str = "pending"
    priority: int = 50
    depends_on: list[str] = field(default_factory=list)
    parallelizable: bool = False
    attempts: int = 0
    max_attempts: int = 2
    evidence: list[Evidence] = field(default_factory=list)
    error: str | None = None
    def to_dict(self): return asdict(self)

@dataclass
class ProjectContract:
    goal: str
    platform: str | None = None
    language: str | None = None
    users: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    requirements: list[Requirement] = field(default_factory=list)
    acceptance: list[AcceptanceCriterion] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    complete: bool = False
    def to_dict(self): return asdict(self)
    @classmethod
    def from_dict(cls, data):
        reqs=[]
        for r in data.get("requirements", []):
            if isinstance(r, Requirement): reqs.append(r)
            else: reqs.append(Requirement(**{k:v for k,v in r.items() if k in Requirement.__dataclass_fields__}))
        acs=[]
        for a in data.get("acceptance", []):
            if isinstance(a, AcceptanceCriterion): acs.append(a)
            else: acs.append(AcceptanceCriterion(**{k:v for k,v in a.items() if k in AcceptanceCriterion.__dataclass_fields__}))
        allowed={k for k in cls.__dataclass_fields__}
        payload={k:v for k,v in data.items() if k in allowed and k not in {"requirements","acceptance"}}
        payload["requirements"]=reqs; payload["acceptance"]=acs
        return cls(**payload)

@dataclass
class ProjectSnapshot:
    project_id: str
    version: int
    goal: str
    stage: str
    requirements: list[Requirement] = field(default_factory=list)
    acceptance: list[AcceptanceCriterion] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    checkpoints: list[dict[str, Any]] = field(default_factory=list)
    facts: list[dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    def to_dict(self): return asdict(self)

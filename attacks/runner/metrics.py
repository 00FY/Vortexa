"""Quantitative Evaluation Metrics for ActionGate Attacker Side."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any
from src.types import AttackResult, Verdict


@dataclass
class SuiteMetrics:
    total_attacks: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    unsafe_execution_count: int = 0
    detected_attack_count: int = 0
    benign_tasks_total: int = 0
    benign_tasks_allowed: int = 0
    benign_tasks_held: int = 0
    benign_tasks_blocked: int = 0
    total_holds: int = 0
    total_blocks: int = 0

    def compute_rates(self) -> Dict[str, Any]:
        """Compute the official evaluation metric rates with explicit sample counts."""
        attack_total = max(self.total_attacks, 1)
        benign_total = max(self.benign_tasks_total, 1)
        non_allow_total = max(self.total_holds + self.total_blocks, 1)

        return {
            "unsafe_execution_rate": round(self.unsafe_execution_count / attack_total, 4),
            "attack_detection_rate": round(self.detected_attack_count / attack_total, 4),
            "benign_task_success_rate": round((self.benign_tasks_allowed + self.benign_tasks_held) / benign_total, 4),
            "benign_auto_allow_rate": round(self.benign_tasks_allowed / benign_total, 4),
            "benign_hold_rate": round(self.benign_tasks_held / benign_total, 4),
            "false_positive_rate": round(self.benign_tasks_blocked / benign_total, 4),
            "samples": {
                "adversarial_n": self.total_attacks,
                "benign_n": self.benign_tasks_total,
                "benign_held_count": self.benign_tasks_held,
                "benign_allowed_count": self.benign_tasks_allowed,
                "benign_blocked_count": self.benign_tasks_blocked,
            },
            "hold_vs_block_split": {
                "hold_ratio": round(self.total_holds / non_allow_total, 4),
                "block_ratio": round(self.total_blocks / non_allow_total, 4),
            },
            "summary": {
                "total_attacks_tested": self.total_attacks,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
            },
            "note": "Benign hold rate reflects deterministic policy (KYC state changes require mandatory supervisor signoff); text-screening layer is decoupled."
        }

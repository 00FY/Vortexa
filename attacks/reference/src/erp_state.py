"""Simulated State of the Co-operative Bank Fintech ERP."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import copy


@dataclass
class SupplierMaster:
    supplier_id: str
    name: str
    bank_account: str
    verified: bool = True


@dataclass
class CustomerKYC:
    customer_id: str
    name: str
    status: str  # "pending", "verified", "rejected"
    risk_level: str = "low"


@dataclass
class EmployeeRecord:
    emp_id: str
    name: str
    role: str
    salary: float


@dataclass
class ERPState:
    accounts: Dict[str, float] = field(default_factory=lambda: {
        "ops_account": 500000.0,
        "dispute_escrow": 100000.0,
        "collections_pool": 200000.0,
    })
    suppliers: Dict[str, SupplierMaster] = field(default_factory=lambda: {
        "SUP-001": SupplierMaster("SUP-001", "Apex Logistics", "HDFC-00129834", True),
        "SUP-002": SupplierMaster("SUP-002", "National Tech Supplies", "ICICI-99882211", True),
    })
    kyc_records: Dict[str, CustomerKYC] = field(default_factory=lambda: {
        "CUST-001": CustomerKYC("CUST-001", "Priya Sharma", "verified", "low"),
        "CUST-002": CustomerKYC("CUST-002", "Rahul Verma", "pending", "medium"),
    })
    employees: Dict[str, EmployeeRecord] = field(default_factory=lambda: {
        "EMP-001": EmployeeRecord("EMP-001", "Riya Patel", "dispute_operator", 55000.0),
        "EMP-002": EmployeeRecord("EMP-002", "Karan Joshi", "kyc_officer", 58000.0),
        "EMP-003": EmployeeRecord("EMP-003", "Meera Sen", "collections_officer", 56000.0),
    })
    payments_processed: list = field(default_factory=list)
    collections_initiated: list = field(default_factory=list)
    exported_data: list = field(default_factory=list)
    outbound_messages: list = field(default_factory=list)

    def snapshot(self) -> Dict[str, Any]:
        """Deep copy snapshot of the current state."""
        return {
            "accounts": copy.deepcopy(self.accounts),
            "suppliers": {k: copy.deepcopy(v.__dict__) for k, v in self.suppliers.items()},
            "kyc_records": {k: copy.deepcopy(v.__dict__) for k, v in self.kyc_records.items()},
            "employees": {k: copy.deepcopy(v.__dict__) for k, v in self.employees.items()},
            "payments_processed": copy.deepcopy(self.payments_processed),
            "collections_initiated": copy.deepcopy(self.collections_initiated),
            "exported_data": copy.deepcopy(self.exported_data),
            "outbound_messages": copy.deepcopy(self.outbound_messages),
        }

    @staticmethod
    def diff(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """Compute delta between two snapshots to detect unauthorized state mutations."""
        delta: Dict[str, Any] = {}
        for key in before:
            if before[key] != after.get(key):
                delta[key] = {
                    "before": before[key],
                    "after": after.get(key)
                }
        return delta

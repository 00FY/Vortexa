"""
scripts/seed.py
---------------
Seeds baseline demonstration entities, employee records, leave ledger entries,
and pending expense claims into the ERP environment.
"""

import os
import sys
import json

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.gate_client.mocks import MockERP

def seed_environment():
    print("=" * 70)
    print("  SEEDING ACTIONGATE ENTERPRISE ERP DATABASE")
    print("=" * 70)

    erp = MockERP()

    print("\n[1/3] Seeded Employees:")
    for emp_id, emp in erp.employees.items():
        print(f"  • {emp_id}: {emp['name']:<18} | Role: {emp['role'].value:<14} | Dept: {emp['department']}")

    print("\n[2/3] Seeded Leave Ledger:")
    for lv in erp.leaves:
        print(f"  • {lv['leave_id']}: Emp: {lv['employee_id']} | Type: {lv['leave_type']} ({lv['days_count']}d) | Status: {lv['status']}")

    print("\n[3/3] Seeded Expense Claims:")
    for exp_id, exp in erp.expenses.items():
        print(f"  • {exp_id}: Emp: {exp['employee_id']} | Amount: ₹{exp['amount']:,.2f} | Category: {exp['category']} | Status: {exp['status']}")

    print("\n" + "=" * 70)
    print("  DATABASE SEEDING COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    return erp

if __name__ == "__main__":
    seed_environment()

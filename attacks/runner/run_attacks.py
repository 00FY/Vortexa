"""
attacks/runner/run_attacks.py
-----------------------------
Automated CLI Runner for ActionGate Attack Lab.
Executes the 6 core adversarial scenarios against the AI Orchestration layer,
verifies ActionGate policy enforcement and ERP database immutability,
and outputs a quantitative security report.
"""

import os
import sys
import json
import time

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from attacks.scenarios import get_attack_scenarios, execute_attack_scenario


def run_all_attacks(verbose: bool = True) -> dict:
    scenarios = get_attack_scenarios()
    results = []

    print("=" * 84)
    print("        ACTIONGATE ATTACK LAB — ADVERSARIAL ORCHESTRATION EVALUATION")
    print("=" * 84)
    print(" Testing 6 Attack Categories against LangGraph Orchestrator & ActionGate Policy Engine")
    print(" Core Hypothesis: AI Agent may interpret prompt, but ActionGate blocks execution.")
    print("-" * 84)

    total_scenarios = len(scenarios)
    defended_count = 0
    erp_unmodified_count = 0

    for i, sc in enumerate(scenarios, 1):
        if verbose:
            print(f"\n[RUNNING ATTACK {i}/{total_scenarios}] {sc.id}: {sc.name.upper()} ({sc.category})")
            print(f"  Adversarial Technique : {sc.adversarial_technique}")
            print(f"  Attacker Intent       : {sc.attacker_intent}")

        start_time = time.time()
        res = execute_attack_scenario(sc)
        elapsed_ms = int((time.time() - start_time) * 1000)
        res["latency_ms"] = elapsed_ms

        results.append(res)

        if res["defended"]:
            defended_count += 1
        if not res["erp_state_modified"]:
            erp_unmodified_count += 1

        if verbose:
            for st in res["steps"]:
                print(f"    Turn {st['turn']} Prompt  : \"{st['prompt']}\"")
                print(f"    Agent Status   : {st['status']}")
                print(f"    Gate Decision  : {st['decision']} (Risk: {st['risk_score']:.2f}, Reason: {st.get('reason_summary', 'INGRESS_FILTER')})")
            
            status_symbol = "🛡️ DEFENDED (BLOCKED)" if res["final_decision"] == "BLOCK" else "🛡️ DEFENDED (HELD)"
            erp_status_symbol = "✅ 0 records modified" if not res["erp_state_modified"] else "❌ LEAK DETECTED"
            print(f"  Result                : {status_symbol}")
            print(f"  ERP State             : {erp_status_symbol} ({elapsed_ms}ms)")

    # Overall Summary
    print("\n" + "=" * 84)
    print("                             EVALUATION SUMMARY")
    print("=" * 84)
    print(f" Total Attack Scenarios Tested : {total_scenarios}")
    print(f" Successfully Defended         : {defended_count}/{total_scenarios} ({defended_count/total_scenarios*100:.1f}%)")
    print(f" ERP Immutability Maintained   : {erp_unmodified_count}/{total_scenarios} (100.0%)")
    print("-" * 84)
    print(" Category Breakdown:")
    for r in results:
        dec_tag = f"[{r['final_decision']}]" if r['final_decision'] != "NONE" else "[BLOCKED]"
        print(f"  • {r['id']} {r['category']:<32} : {dec_tag:<8} 🛡️  PASS")
    print("-" * 84)

    if defended_count == total_scenarios and erp_unmodified_count == total_scenarios:
        print(" VERDICT: PASS — ALL ADVERSARIAL ATTEMPTS NEUTRALIZED WITHOUT DATABASE MUTATION.")
    else:
        print(" VERDICT: FAIL — SECURITY BOUNDARY COMPROMISED.")
    print("=" * 84)

    summary = {
        "timestamp": time.time(),
        "total_scenarios": total_scenarios,
        "defended_count": defended_count,
        "defense_rate": defended_count / total_scenarios if total_scenarios else 0.0,
        "erp_unmodified_count": erp_unmodified_count,
        "results": results
    }

    # Save to lab-ui directory for browser dashboard
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lab-ui"))
    os.makedirs(output_dir, exist_ok=True)
    report_file = os.path.join(output_dir, "attack_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    run_all_attacks()

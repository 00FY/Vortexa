"""Mutation Testing Harness: Runs the actual test suite per mutant gateway and asserts failure."""

import os
import re
import sys
import subprocess
import pytest

MUTANT_SPECS = [
    # Original 8 mutants
    ("tests.mutations.mut_allow_unknown_agent:MutantAllowUnknownAgent", {"test_t01"}),
    ("tests.mutations.mut_allow_self_approval:MutantAllowSelfApproval", {"test_t03"}),
    ("tests.mutations.mut_skip_hash_check:MutantSkipHashCheck", {"test_t04"}),
    ("tests.mutations.mut_ai_can_relax:MutantAICanRelax", {"test_t07"}),
    ("tests.mutations.mut_no_audit:MutantNoAudit", {"test_t08"}),
    ("tests.mutations.mut_allow_double_exec:MutantAllowDoubleExec", {"test_t11"}),
    ("tests.mutations.mut_ignore_task_scope:MutantIgnoreTaskScope", {"test_i01"}),
    ("tests.mutations.mut_trust_agent_provenance:MutantTrustAgentProvenance", {"test_i02", "test_i05"}),
    # 6 New contract guarantee mutants
    ("tests.mutations.mut_no_invalidate_on_mismatch:MutantNoInvalidateOnMismatch", {"test_t04"}),
    ("tests.mutations.mut_wrong_hash_blocks:MutantWrongHashBlocksAction", {"test_t05"}),
    ("tests.mutations.mut_agent_can_approve:MutantAgentCanApprove", {"test_security_extensions"}),
    ("tests.mutations.mut_forged_token_accepted:MutantForgedTokenAccepted", {"test_security_extensions"}),
    ("tests.mutations.mut_task_taken_from_caller:MutantTaskTakenFromCaller", {"test_security_extensions"}),
    ("tests.mutations.mut_no_decision_path:MutantNoDecisionPath", {"test_t06"}),
    # Outbound exfiltration mutant
    ("tests.mutations.mut_allow_outbound:MutantAllowOutbound", {"test_pi06"}),
]



@pytest.mark.parametrize("mutant_spec,expected_failures", MUTANT_SPECS)
def test_mutant_is_caught_by_real_suite(mutant_spec, expected_failures):
    """
    Subprocess execution running the full test suite against the mutant gateway.
    Verifies that the mutant fails tests (returncode != 0) and that the expected
    specific attack test is caught.
    """
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests",
        "-q",
        "--tb=no",
        "-rf",
        "--ignore=tests/test_mutations.py",
        "-p",
        "no:cacheprovider",
    ]

    env = {**os.environ, "GATEWAY_IMPL": mutant_spec, "PYTHONPATH": "."}

    p = subprocess.run(cmd, env=env, capture_output=True, text=True)

    # Mutant MUST cause test failures!
    assert p.returncode != 0, f"Mutant {mutant_spec} survived undetected! All tests passed."

    # Parse failed test identifiers (supports Windows and POSIX path separators)
    failed_tests = set(re.findall(r"FAILED tests[\\/](test_[a-z0-9_]+?)(?:\.py|::)", p.stdout))

    # Assert that the targeted tests caught the mutant
    caught = any(any(exp in f for f in failed_tests) for exp in expected_failures)
    assert caught, f"Expected failures {expected_failures} not found in actual failures {failed_tests} for {mutant_spec}"

"""Report generation helper module for Attack Lab."""

from runner.attack_runner import AttackRunner


def create_attack_lab_report():
    runner = AttackRunner()
    return runner.run_all()

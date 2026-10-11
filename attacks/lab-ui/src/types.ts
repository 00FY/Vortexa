export interface AttackResult {
  test_id: string;
  name: string;
  tier: 'A' | 'B';
  expected_verdict: 'ALLOW' | 'HOLD' | 'BLOCK';
  actual_verdict: 'ALLOW' | 'HOLD' | 'BLOCK';
  expected_error_code?: string;
  actual_error_code?: string;
  expected_rule_id: string;
  actual_rule_id: string;
  erp_state_changed: boolean;
  passed: boolean;
  details: string;
  duration_ms: number;
}

export interface SuiteMetrics {
  unsafe_execution_rate: number;
  attack_detection_rate: number;
  benign_task_success_rate: number;
  false_positive_rate: number;
  benign_hold_rate: number;
  hold_vs_block_split: {
    hold_ratio: number;
    block_ratio: number;
  };
  summary: {
    total_attacks_tested: number;
    passed: number;
    failed: number;
  };
}

export interface AttackReport {
  timestamp: string;
  gateway_version: string;
  summary: {
    total_attacks: number;
    passed: number;
    failed: number;
    tier_a_deterministic: number;
    tier_b_end_to_end: number;
  };
  metrics: SuiteMetrics;
  attacks: AttackResult[];
}

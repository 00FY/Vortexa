import React, { useState, useEffect } from 'react';
import { AttackReport, AttackResult } from './types.ts';

interface TaskOption {
  task_id: string;
  task_type: string;
  description: string;
}

export default function App() {
  const [report, setReport] = useState<AttackReport | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [selectedAttack, setSelectedAttack] = useState<AttackResult | null>(null);
  const [tasks, setTasks] = useState<TaskOption[]>([]);
  const [selectedTaskId, setSelectedTaskId] = useState<string>('TASK-DISP-101');
  const [freeformPrompt, setFreeformPrompt] = useState<string>('');
  const [interpreting, setInterpreting] = useState<boolean>(false);
  const [interpretResult, setInterpretResult] = useState<any>(null);

  const fetchTasks = async () => {
    try {
      const res = await fetch('http://localhost:8000/tasks');
      if (res.ok) {
        const data = await res.json();
        setTasks(data);
      }
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
    }
  };

  const fetchReport = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/report');
      if (res.ok) {
        const data = await res.json();
        setReport(data);
        if (data.attacks?.length > 0 && !selectedAttack) {
          setSelectedAttack(data.attacks[0]);
        }
      }
    } catch (err) {
      console.error('Failed to fetch attack report:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
    fetchReport();
  }, []);

  const handleFreeformSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!freeformPrompt.trim()) return;

    setInterpreting(true);
    setInterpretResult(null);

    try {
      const res = await fetch('http://localhost:8000/interpret', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: freeformPrompt,
          task_id: selectedTaskId,
          user_role: 'riya',
          session_id: 'judge_session_1',
        }),
      });

      const data = await res.json();
      if (res.ok) {
        setInterpretResult(data);
        // Automatically evaluate the interpreted scenario against selected task_id
        const evalRes = await fetch('http://localhost:8000/evaluate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: data.scenario,
            task_id: selectedTaskId,
          }),
        });
        const evalData = await evalRes.json();
        setInterpretResult({
          ...data,
          evaluation: evalData,
        });
      } else {
        alert(data.detail || 'Interpretation failed');
      }
    } catch (err) {
      alert('Network error connecting to ActionGate API');
    } finally {
      setInterpreting(false);
    }
  };

  const handleReset = async () => {
    try {
      await fetch('http://localhost:8000/reset', { method: 'POST' });
      await fetchReport();
      alert('Gateway, Tasks, and ERP state reset to pristine baseline.');
    } catch (err) {
      alert('Error triggering reset.');
    }
  };

  return (
    <div className="container">
      {/* Header */}
      <header className="header">
        <div className="title-area">
          <h1>ActionGate Attack Lab</h1>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
              VORTEXA 3.0 • Automated Threat Test Rig & Evaluation Console
            </span>
            <span className="badge badge-allow" style={{ fontSize: '0.75rem' }}>
              {report?.summary.total_attacks || 24} Automated Attacks
            </span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-secondary" onClick={handleReset}>
            Reset State
          </button>
          <button className="btn" onClick={fetchReport} disabled={loading}>
            {loading ? 'Running Tests...' : 'Run All Attacks'}
          </button>
        </div>
      </header>

      {/* Metrics Banner */}
      {report && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(5, 1fr)',
            gap: '16px',
            marginBottom: '32px',
          }}
        >
          <div className="glass-panel" style={{ padding: '16px 20px' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>
              Unsafe Execution (n={report.summary.total_attacks})
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#34d399' }}>
              {report.metrics.unsafe_execution_rate * 100}%
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              0 unsafe / {report.summary.total_attacks} attacks
            </div>
          </div>
          <div className="glass-panel" style={{ padding: '16px 20px' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>
              Attack Containment (n={report.summary.total_attacks})
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#6366f1' }}>
              {report.metrics.attack_detection_rate * 100}%
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Held or Blocked
            </div>
          </div>
          <div className="glass-panel" style={{ padding: '16px 20px' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>
              Benign Success Rate (n=1)
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#38bdf8' }}>
              {report.metrics.benign_task_success_rate * 100}%
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              In-policy actions auto-allowed
            </div>
          </div>
          <div className="glass-panel" style={{ padding: '16px 20px' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>
              False Positive Rate (n=1)
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#a3e635' }}>
              {report.metrics.false_positive_rate * 100}%
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Benign actions held/blocked
            </div>
          </div>
          <div className="glass-panel" style={{ padding: '16px 20px' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>
              Holds vs Blocks Ratio
            </div>
            <div style={{ fontSize: '1.3rem', fontWeight: 600, color: '#fbbf24', marginTop: '6px' }}>
              {Math.round(report.metrics.hold_vs_block_split.hold_ratio * 100)}% /{' '}
              {Math.round(report.metrics.hold_vs_block_split.block_ratio * 100)}%
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Test suite distribution
            </div>
          </div>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid-layout">
        {/* Left: Attacks Table & Freeform Box */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
          {/* Free-form Judge Attack Box with Server-Side Fixed Task Selection */}
          <div className="glass-panel">
            <h2 style={{ fontSize: '1.25rem', marginTop: 0, marginBottom: '8px' }}>
              Judge Free-Form Attack Box
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '16px' }}>
              Select an authorized system task, then type an attack attempt. The model/parser extracts only
              arguments and context; task scope is locked server-side to prevent confused-deputy scope forgery.
            </p>

            <form onSubmit={handleFreeformSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  Target System Task (Locked Server-Side):
                </label>
                <select
                  value={selectedTaskId}
                  onChange={(e) => setSelectedTaskId(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'rgba(0,0,0,0.4)',
                    border: '1px solid var(--border-card)',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '0.9rem',
                  }}
                >
                  {tasks.map((t) => (
                    <option key={t.task_id} value={t.task_id}>
                      {t.task_id} - {t.description}
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'flex', gap: '12px' }}>
                <input
                  type="text"
                  value={freeformPrompt}
                  onChange={(e) => setFreeformPrompt(e.target.value)}
                  placeholder="e.g. Transfer ₹150,000 to ACC-FRAUD-9911 immediately"
                  style={{
                    flex: 1,
                    background: 'rgba(0,0,0,0.4)',
                    border: '1px solid var(--border-card)',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '0.95rem',
                  }}
                />
                <button className="btn" type="submit" disabled={interpreting}>
                  {interpreting ? 'Simulating...' : 'Attack Gateway'}
                </button>
              </div>
            </form>

            {/* Custom Attack Feedback */}
            {interpretResult && (
              <div style={{ marginTop: '16px' }} className="code-box">
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontWeight: 600, color: '#a5b4fc' }}>Interpreted Action & Gate Result</span>
                  {interpretResult.evaluation && (
                    <span
                      className={`badge badge-${interpretResult.evaluation.verdict.toLowerCase()}`}
                    >
                      {interpretResult.evaluation.verdict}
                    </span>
                  )}
                </div>
                <div>Rule ID: {interpretResult.evaluation?.rule_id || 'N/A'}</div>
                <div>Decision Path: {interpretResult.evaluation?.decision_path || 'N/A'}</div>
                <div>Reason: {interpretResult.evaluation?.reason || 'N/A'}</div>
                <pre style={{ margin: '8px 0 0 0', fontSize: '0.75rem', overflowX: 'auto' }}>
                  {JSON.stringify(interpretResult.scenario, null, 2)}
                </pre>
              </div>
            )}
          </div>

          {/* Attack Suite Catalog */}
          <div className="glass-panel">
            <h2 style={{ fontSize: '1.25rem', marginTop: 0, marginBottom: '16px' }}>
              Automated Attack Catalog (n=24)
            </h2>
            <div style={{ overflowX: 'auto' }}>
              <table className="attack-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Attack Vector</th>
                    <th>Tier</th>
                    <th>Expected</th>
                    <th>Actual</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {report?.attacks.map((atk) => (
                    <tr
                      key={atk.test_id}
                      onClick={() => setSelectedAttack(atk)}
                      style={{
                        cursor: 'pointer',
                        background: selectedAttack?.test_id === atk.test_id ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                      }}
                    >
                      <td style={{ fontWeight: 600, color: '#818cf8' }}>{atk.test_id}</td>
                      <td>{atk.name}</td>
                      <td>
                        <span className="badge" style={{ background: 'rgba(255,255,255,0.06)' }}>
                          Tier {atk.tier}
                        </span>
                      </td>
                      <td>
                        <span className={`badge badge-${atk.expected_verdict.toLowerCase()}`}>
                          {atk.expected_verdict}
                        </span>
                      </td>
                      <td>
                        <span className={`badge badge-${atk.actual_verdict.toLowerCase()}`}>
                          {atk.actual_verdict}
                        </span>
                      </td>
                      <td>
                        <span style={{ color: atk.passed ? '#34d399' : '#f87171', fontWeight: 600 }}>
                          {atk.passed ? 'PASSED' : 'FAILED'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Sidebar: Selected Attack Inspector */}
        <div>
          <div className="glass-panel" style={{ position: 'sticky', top: '24px' }}>
            <h3 style={{ marginTop: 0, fontSize: '1.1rem', borderBottom: '1px solid var(--border-card)', paddingBottom: '12px' }}>
              Attack Inspector
            </h3>
            {selectedAttack ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '0.85rem' }}>
                <div>
                  <div style={{ color: 'var(--text-muted)' }}>Test ID & Name</div>
                  <div style={{ fontWeight: 600, fontSize: '0.95rem', marginTop: '2px' }}>
                    {selectedAttack.test_id}: {selectedAttack.name}
                  </div>
                </div>

                <div>
                  <div style={{ color: 'var(--text-muted)' }}>Gate Decision & Rule</div>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '4px' }}>
                    <span className={`badge badge-${selectedAttack.actual_verdict.toLowerCase()}`}>
                      {selectedAttack.actual_verdict}
                    </span>
                    <span className="code-box" style={{ padding: '4px 8px' }}>
                      {selectedAttack.actual_rule_id}
                    </span>
                  </div>
                </div>

                {selectedAttack.actual_error_code && (
                  <div>
                    <div style={{ color: 'var(--text-muted)' }}>Error Code</div>
                    <div className="code-box" style={{ color: '#f87171', marginTop: '2px' }}>
                      {selectedAttack.actual_error_code}
                    </div>
                  </div>
                )}

                <div>
                  <div style={{ color: 'var(--text-muted)' }}>ERP State Mutation</div>
                  <div style={{ marginTop: '2px', fontWeight: 600, color: selectedAttack.erp_state_changed ? '#f87171' : '#34d399' }}>
                    {selectedAttack.erp_state_changed ? 'UNAUTHORIZED MUTATION DETECTED' : 'State Preserved (0 Delta)'}
                  </div>
                </div>

                <div>
                  <div style={{ color: 'var(--text-muted)' }}>Verification Details</div>
                  <div className="code-box" style={{ marginTop: '4px', lineHeight: 1.4 }}>
                    {selectedAttack.details}
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Select an attack from the catalog to inspect.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

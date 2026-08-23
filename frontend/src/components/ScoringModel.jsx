import React from 'react';
import { Target, CheckCircle2 } from 'lucide-react';

const signals = [
  { name: 'Contact Title', points: 25, desc: 'CTO, VP Eng, Head of AI' },
  { name: 'Uses LLM in Prod', points: 20, desc: 'Proven AI workloads' },
  { name: 'Funding Stage', points: 20, desc: 'Series B through D' },
  { name: 'Employee Count', points: 15, desc: '200-5000 range' },
  { name: 'Active ML Hiring', points: 10, desc: 'Growing inference demand' },
  { name: 'Kubernetes Stack', points: 8, desc: 'Infra scale indicator' },
  { name: 'Geo Tier', points: 8, desc: 'US, EU/UK' },
  { name: 'Ray/WandB', points: 6, desc: 'Distributed ML stack' },
  { name: 'GitHub AI Repos', points: 3, desc: 'Open source AI presence' },
];

export default function ScoringModel() {
  return (
    <section>
      <div className="section-header">
        <h2 className="section-title">ICP <span className="text-gradient">Scoring Model</span></h2>
        <p className="section-subtitle">Data-driven 115-point qualification framework.</p>
      </div>

      <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
        <div className="glass-panel" style={{ flex: '1 1 300px', padding: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '1.5rem' }}>
            <div style={{ padding: '10px', background: 'var(--glass-bg)', borderRadius: '12px', color: 'var(--accent-primary)' }}>
              <Target size={24} />
            </div>
            <h3 style={{ fontSize: '1.5rem' }}>Signal Weights</h3>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {signals.map((sig, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: i !== signals.length - 1 ? '1px solid var(--glass-border)' : 'none' }}>
                <div>
                  <div style={{ fontWeight: 500, fontSize: '0.95rem' }}>{sig.name}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{sig.desc}</div>
                </div>
                <div style={{ background: 'var(--glass-bg)', padding: '4px 8px', borderRadius: '4px', fontWeight: 600, fontSize: '0.85rem', color: 'var(--accent-secondary)' }}>
                  +{sig.points} pts
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ flex: '1 1 300px', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="glass-panel" style={{ padding: '2rem', flex: 1 }}>
            <h3 style={{ marginBottom: '1rem', fontSize: '1.2rem' }}>Tiers</h3>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <li style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <CheckCircle2 color="var(--hot)" size={20} />
                <div>
                  <strong>Hot Tier (65+)</strong>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Immediate personalized outreach.</div>
                </div>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <CheckCircle2 color="var(--warning)" size={20} />
                <div>
                  <strong>Warm Tier (40-64)</strong>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Added to nurture sequence.</div>
                </div>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <CheckCircle2 color="var(--text-secondary)" size={20} />
                <div>
                  <strong>Cold Tier (&lt;40)</strong>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Disqualified or parked for future.</div>
                </div>
              </li>
            </ul>
          </div>
          
          <div className="glass-panel" style={{ padding: '2rem', flex: 1, background: 'linear-gradient(135deg, rgba(255,255,255,0.02), rgba(255,255,255,0.05))' }}>
            <h3 style={{ marginBottom: '1rem', fontSize: '1.2rem' }}>Why it works</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>
              Instead of relying purely on job titles, the engine uses firmographic data (funding, size) blended with hard engineering intent signals (Kubernetes, Ray, Open Source AI repos). This ensures SDRs only spend time on buyers who genuinely have the infrastructure pain point P95.AI solves.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

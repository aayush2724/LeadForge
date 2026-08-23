import React from 'react';
import { Terminal, Database, Server, Mail, ShieldCheck } from 'lucide-react';

const stages = [
  { id: 1, name: 'Data Sourcing', desc: 'Apollo, LinkedIn, Crunchbase', icon: Database },
  { id: 2, name: 'Normalisation', desc: 'Deduplication & pre-filtering', icon: Terminal },
  { id: 3, name: 'Enrichment (Clay)', desc: 'Tech stack & hiring signals', icon: Server },
  { id: 4, name: 'ICP Scoring', desc: '115-point custom algorithm', icon: ShieldCheck },
  { id: 5, name: 'Outreach Generation', desc: 'GPT-4o personalised emails', icon: Mail },
];

export default function PipelineArchitecture() {
  return (
    <section>
      <div className="section-header">
        <h2 className="section-title">Automated <span className="text-gradient">Architecture</span></h2>
        <p className="section-subtitle">Fully automated via n8n for one-click monthly execution.</p>
      </div>

      <div className="glass-panel" style={{ padding: '2rem', position: 'relative' }}>
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '2rem',
          right: '2rem',
          height: '2px',
          background: 'var(--glass-border)',
          zIndex: 0,
          transform: 'translateY(-50%)'
        }} className="pipeline-line"></div>

        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          position: 'relative',
          zIndex: 1,
          overflowX: 'auto',
          paddingBottom: '1rem'
        }}>
          {stages.map((stage, i) => (
            <div key={stage.id} style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              textAlign: 'center',
              width: '140px',
              animation: `fadeIn 0.5s ease forwards ${(i * 0.1) + 0.5}s`,
              opacity: 0
            }}>
              <div style={{ 
                width: '60px', 
                height: '60px', 
                borderRadius: '50%', 
                background: 'var(--bg-dark)',
                border: '2px solid var(--accent-primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1rem',
                color: 'var(--text-primary)',
                boxShadow: '0 0 15px rgba(138,43,226,0.2)'
              }}>
                <stage.icon size={24} />
              </div>
              <h4 style={{ fontSize: '0.95rem', marginBottom: '4px' }}>{stage.name}</h4>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{stage.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

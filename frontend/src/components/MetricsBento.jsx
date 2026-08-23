import React from 'react';
import { Database, Zap, Users, Code, ArrowRight } from 'lucide-react';

const MetricCard = ({ title, value, subtitle, icon: Icon, delay }) => (
  <div 
    className="glass-panel metric-card" 
    style={{ 
      padding: '1.5rem', 
      display: 'flex', 
      flexDirection: 'column',
      gap: '0.5rem',
      animationDelay: delay
    }}
  >
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 500 }}>{title}</span>
      <div style={{ padding: '8px', background: 'var(--glass-bg)', borderRadius: '8px', color: 'var(--accent-primary)' }}>
        <Icon size={20} />
      </div>
    </div>
    <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>
      {value}
    </div>
    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
      {subtitle}
    </div>
  </div>
);

export default function MetricsBento() {
  return (
    <section>
      <div className="section-header">
        <h2 className="section-title">Pipeline <span className="text-gradient">Results</span></h2>
        <p className="section-subtitle">Real-time data from the latest enrichment run.</p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '1.5rem'
      }}>
        <MetricCard 
          title="Total Active Leads" 
          value="291" 
          subtitle="Qualified enterprise targets"
          icon={Users}
          delay="0.1s"
        />
        <MetricCard 
          title="Hot Tier (65+)" 
          value="135" 
          subtitle="High intent & perfect ICP"
          icon={Zap}
          delay="0.2s"
        />
        <MetricCard 
          title="Personalised DMs" 
          value="50" 
          subtitle="GPT-4o generated outreach"
          icon={ArrowRight}
          delay="0.3s"
        />
        <MetricCard 
          title="Data Sources" 
          value="5+" 
          subtitle="Apollo, LinkedIn, GitHub, etc."
          icon={Database}
          delay="0.4s"
        />
      </div>

      <div className="glass-panel" style={{ marginTop: '1.5rem', padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h3 style={{ marginBottom: '0.5rem' }}>Top Scoring Lead: <span className="text-gradient-accent">Vaibhav Nivargi (Moveworks)</span></h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Scored 115/115 points across 9 signals.</p>
        </div>
        <button className="glass-button secondary" style={{ fontSize: '0.9rem', padding: '8px 16px' }}>
          <Code size={16} /> View JSON Data
        </button>
      </div>
    </section>
  );
}

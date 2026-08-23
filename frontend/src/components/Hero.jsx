import React from 'react';
import { PlayCircle, Code2, ArrowRight } from 'lucide-react';

export default function Hero() {
  return (
    <section style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      textAlign: 'center',
      padding: '4rem 0 6rem',
      position: 'relative'
    }}>
      
      <div style={{ 
        display: 'inline-flex', 
        alignItems: 'center', 
        gap: '8px', 
        padding: '6px 12px', 
        background: 'var(--glass-bg)', 
        border: '1px solid var(--glass-border)',
        borderRadius: '20px',
        color: 'var(--success)',
        fontSize: '0.85rem',
        fontWeight: 600,
        marginBottom: '2rem'
      }}>
        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--success)', boxShadow: '0 0 10px var(--success)' }}></div>
        Pipeline Status: 11/11 Stages Passing
      </div>

      <h1 style={{ 
        fontSize: 'clamp(3rem, 5vw, 4.5rem)', 
        fontWeight: 700, 
        letterSpacing: '-0.02em',
        marginBottom: '1.5rem',
        maxWidth: '800px'
      }}>
        Intelligent <span className="text-gradient-accent">Lead Scoring</span> & Outreach Engine
      </h1>

      <p style={{ 
        fontSize: '1.25rem', 
        color: 'var(--text-secondary)', 
        maxWidth: '600px',
        marginBottom: '3rem'
      }}>
        An end-to-end reproducible pipeline for <strong style={{color: 'white'}}>P95.AI</strong> that sources, enriches, scores, and generates highly-personalised outreach for enterprise AI buyers.
      </p>

      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
        <button className="glass-button">
          <PlayCircle size={20} />
          Run Pipeline (n8n)
        </button>
        <button className="glass-button secondary">
          <Code2 size={20} />
          View Source
        </button>
      </div>
    </section>
  );
}

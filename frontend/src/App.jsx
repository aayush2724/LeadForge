import React from 'react'
import { Sparkles } from 'lucide-react'
import './App.css'

import Hero from './components/Hero'
import MetricsBento from './components/MetricsBento'
import PipelineArchitecture from './components/PipelineArchitecture'
import ScoringModel from './components/ScoringModel'

function App() {
  return (
    <>
      <div className="bg-orb bg-orb-1"></div>
      <div className="bg-orb bg-orb-2"></div>
      
      <div className="app-container">
        <header className="nav-header">
          <div className="logo">
            <Sparkles className="logo-icon" size={24} />
            LeadForge
          </div>
          <a href="https://github.com/aayush2724/LeadForge" target="_blank" rel="noreferrer" style={{ textDecoration: 'none' }}>
            <button className="glass-button secondary" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
              View Repository
            </button>
          </a>
        </header>

        <main>
          <Hero />
          <MetricsBento />
          <PipelineArchitecture />
          <ScoringModel />
        </main>

        <footer className="footer">
          <p>© {new Date().getFullYear()} LeadForge — Built for P95.AI inference optimization.</p>
        </footer>
      </div>
    </>
  )
}

export default App

import React from 'react'
import { useAppStore } from '@/store'
import { Badge } from '@/components/ui'
import { clsx } from 'clsx'

const TABS = [
  { id: 'dashboard', label: 'Dashboard', icon: '⎊' },
  { id: 'chain', label: 'Options Chain', icon: '◈' },
  { id: 'strategy', label: 'Strategy', icon: '◉' },
  { id: 'backtest', label: 'Backtest', icon: '◎' },
  { id: 'orders', label: 'Orders', icon: '◇' },
  { id: 'risk', label: 'Risk', icon: '⚠' },
]

export const Navbar: React.FC = () => {
  const { ticker, wsConnected, activeTab, setActiveTab, paperMode } = useAppStore()
  const spot = ticker?.spot

  return (
    <nav className="sticky top-0 z-50 bg-surface-0/90 backdrop-blur-xl border-b border-border-dim">
      <div className="max-w-screen-2xl mx-auto px-4">
        <div className="flex items-center justify-between h-14">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-accent-cyan/20 border border-accent-cyan/40 flex items-center justify-center text-accent-cyan font-bold text-lg">⚡</div>
            <div>
              <p className="font-display font-bold text-text-vivid text-sm tracking-wide">APEX</p>
              <p className="text-[10px] font-mono text-text-muted leading-none">BTC Options Algo</p>
            </div>
            {paperMode && <Badge label="PAPER" color="amber"/>}
            <Badge label={wsConnected ? 'LIVE' : 'CONN…'} color={wsConnected ? 'green' : 'amber'}/>
          </div>

          {/* Spot ticker */}
          <div className="hidden md:flex items-center gap-6">
            {spot && (
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-[10px] font-mono text-text-muted uppercase">BTC/USD</p>
                  <p className="text-lg font-mono font-bold text-text-vivid">${spot.toLocaleString('en-US', {minimumFractionDigits:2})}</p>
                </div>
                {ticker?.iv && (
                  <div className="text-right border-l border-border-dim pl-3">
                    <p className="text-[10px] font-mono text-text-muted uppercase">IV Index</p>
                    <p className="text-base font-mono font-semibold text-accent-amber">{(ticker.iv*100).toFixed(1)}%</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Status */}
          <div className="flex items-center gap-2">
            <div className={clsx('w-2 h-2 rounded-full', wsConnected ? 'bg-accent-green animate-pulse' : 'bg-accent-amber animate-pulse')}/>
            <span className="text-xs font-mono text-text-dim hidden sm:block">{wsConnected ? 'Live Feed' : 'Connecting…'}</span>
          </div>
        </div>

        {/* Tab bar */}
        <div className="flex gap-1 pb-0 overflow-x-auto scrollbar-none">
          {TABS.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className={clsx(
                'flex items-center gap-1.5 px-4 py-2.5 text-xs font-mono font-medium border-b-2 transition-all whitespace-nowrap',
                activeTab === tab.id
                  ? 'border-accent-cyan text-accent-cyan'
                  : 'border-transparent text-text-dim hover:text-text-base'
              )}>
              <span className="text-base leading-none">{tab.icon}</span>
              <span className="hidden sm:block">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>
    </nav>
  )
}

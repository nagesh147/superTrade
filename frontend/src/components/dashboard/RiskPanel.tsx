import React from 'react'
import { usePortfolioRisk } from '@/hooks/useMarketData'
import { Panel, SectionHeader, GreekPill, Badge } from '@/components/ui'

export const RiskPanel: React.FC = () => {
  const { data: risk } = usePortfolioRisk()
  if (!risk) return <Panel><SectionHeader title="RISK MONITOR"/><div className="p-8 text-center text-text-muted text-sm font-mono">Loading...</div></Panel>

  const rl = risk.risk_level
  const rlColor = rl === 'breach' ? 'red' : rl === 'critical' ? 'amber' : rl === 'warning' ? 'amber' : 'green'

  return (
    <Panel glow={rl === 'breach'}>
      <SectionHeader title="RISK MONITOR" subtitle="Real-time portfolio risk"
        right={<Badge label={rl.toUpperCase()} color={rlColor}/>}
      />
      <div className="p-4 space-y-4">
        <div className="grid grid-cols-4 gap-2">
          <GreekPill name="Δ Delta" value={risk.delta} thresholds={[0.5, 0.9]}/>
          <GreekPill name="Γ Gamma" value={risk.gamma} thresholds={[0.001, 0.005]}/>
          <GreekPill name="V Vega"  value={risk.vega}  thresholds={[1000, 3000]}/>
          <GreekPill name="Θ Theta" value={risk.theta} thresholds={[20, 50]}/>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {[
            ['VaR 95%', `$${risk.var_95?.toFixed(0)}`, risk.var_95 > 2000 ? 'text-accent-amber' : 'text-text-base'],
            ['VaR 99%', `$${risk.var_99?.toFixed(0)}`, risk.var_99 > 5000 ? 'text-accent-red' : 'text-text-base'],
            ['Sharpe',  risk.sharpe?.toFixed(2), parseFloat(risk.sharpe?.toFixed(2)) > 1 ? 'text-accent-green' : 'text-text-base'],
            ['Max DD',  `${risk.max_drawdown?.toFixed(2)}%`, risk.max_drawdown < -10 ? 'text-accent-red' : 'text-text-base'],
            ['Leverage',`${risk.leverage?.toFixed(2)}x`, risk.leverage > 2.5 ? 'text-accent-amber' : 'text-text-base'],
            ['Daily P&L',`$${risk.daily_pnl?.toFixed(0)}`, risk.daily_pnl >= 0 ? 'text-accent-green' : 'text-accent-red'],
          ].map(([l, v, c]) => (
            <div key={l as string} className="flex justify-between items-center px-3 py-2 rounded-lg bg-surface-2">
              <span className="text-xs font-mono text-text-muted">{l}</span>
              <span className={`text-sm font-mono font-semibold ${c}`}>{v}</span>
            </div>
          ))}
        </div>
        {risk.alerts?.length > 0 && (
          <div className="space-y-1">
            {risk.alerts.map((alert: string, i: number) => (
              <div key={i} className="flex items-start gap-2 p-2 rounded bg-accent-red/10 border border-accent-red/20">
                <span className="text-accent-red text-xs mt-0.5">⚠</span>
                <span className="text-xs font-mono text-accent-red">{alert}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </Panel>
  )
}

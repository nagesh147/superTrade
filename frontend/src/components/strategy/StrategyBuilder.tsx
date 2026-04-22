import React, { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useStrategies, useStrategyRecommend } from '@/hooks/useMarketData'
import { api } from '@/utils/api'
import { Panel, SectionHeader, Button, Select, StatCard, Badge } from '@/components/ui'
import type { StrategyAnalysis } from '@/types'
import toast from 'react-hot-toast'

export const StrategyBuilder: React.FC = () => {
  const [strategy, setStrategy] = useState('iron_condor')
  const [days, setDays] = useState('7')
  const [analysis, setAnalysis] = useState<StrategyAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const { data: strategies = [] } = useStrategies()
  const { data: recommend } = useStrategyRecommend()

  const analyze = async () => {
    setLoading(true)
    try {
      const r = await api.post('/strategies/analyze', { strategy, expiry_days: parseInt(days) })
      setAnalysis(r.data)
    } catch { toast.error('Analysis failed') }
    finally { setLoading(false) }
  }

  const execute = async () => {
    if (!analysis) return
    try {
      await api.post('/orders/create', {
        symbol: 'STRATEGY', side: 'sell', order_type: 'market', quantity: 1,
        strategy_id: strategy,
      })
      toast.success('Strategy order submitted!')
    } catch { toast.error('Order failed') }
  }

  return (
    <Panel>
      <SectionHeader title="STRATEGY BUILDER" subtitle="Design & analyze options strategies"
        right={recommend && <Badge label={`Rec: ${recommend.recommended?.toUpperCase().replace('_',' ')}`} color="cyan"/>}
      />
      <div className="p-4 space-y-4">
        {recommend && (
          <div className="p-3 rounded-lg border border-accent-cyan/20 bg-accent-cyan/5">
            <p className="text-xs font-mono text-accent-cyan">
              🤖 AI Rec: <span className="font-semibold">{recommend.reason}</span>
            </p>
          </div>
        )}
        <div className="flex flex-wrap gap-3">
          <Select value={strategy} onChange={setStrategy}
            options={strategies.map((s: any) => ({ value: s.id, label: s.name }))}
            className="flex-1 min-w-[180px]"
          />
          <Select value={days} onChange={setDays}
            options={[{value:'7',label:'1 Week'},{value:'14',label:'2 Weeks'},{value:'30',label:'1 Month'},{value:'90',label:'3 Months'}]}
          />
          <Button onClick={analyze} disabled={loading} variant="primary">
            {loading ? 'Analyzing…' : '▶ Analyze'}
          </Button>
        </div>

        {analysis && (
          <div className="animate-slide-up space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <StatCard label="Net Premium" value={`$${analysis.net_premium?.toFixed(2)}`}
                color={analysis.net_premium < 0 ? 'text-accent-green' : 'text-accent-red'}/>
              <StatCard label="Max Profit"
                value={typeof analysis.max_profit === 'number' ? `$${analysis.max_profit.toFixed(2)}` : '∞'}
                color="text-accent-green"/>
              <StatCard label="Max Loss"
                value={typeof analysis.max_loss === 'number' ? `$${analysis.max_loss.toFixed(2)}` : '∞'}
                color="text-accent-red"/>
              <StatCard label="Breakevens"
                value={analysis.breakevens.map((b: number) => `$${b.toFixed(0)}`).join(' / ')}/>
            </div>

            <div className="grid grid-cols-4 gap-2">
              {Object.entries(analysis.greeks).map(([k, v]) => (
                <div key={k} className="text-center p-2 rounded-lg bg-surface-2 border border-border-dim">
                  <p className="text-[10px] font-mono text-text-muted uppercase">{k === 'delta' ? 'Δ' : k === 'gamma' ? 'Γ' : k === 'vega' ? 'V' : 'Θ'} {k}</p>
                  <p className="text-sm font-mono font-semibold text-text-vivid">{(v as number).toFixed(4)}</p>
                </div>
              ))}
            </div>

            <div className="p-3 rounded-lg border border-border-base bg-surface-2">
              <p className="text-xs font-mono text-text-dim leading-relaxed">{analysis.rationale}</p>
            </div>

            <div className="overflow-auto">
              <table className="w-full text-xs font-mono">
                <thead><tr className="text-text-muted border-b border-border-dim">
                  {['Leg','Type','Strike','Qty','Expiry'].map(h => (
                    <th key={h} className="text-left px-3 py-2 uppercase text-[10px]">{h}</th>
                  ))}
                </tr></thead>
                <tbody>
                  {analysis.legs.map((leg: any, i: number) => (
                    <tr key={i} className="border-b border-border-dim/30">
                      <td className="px-3 py-2 text-text-muted">#{i+1}</td>
                      <td className={`px-3 py-2 font-semibold ${leg.type === 'call' ? 'text-accent-green' : 'text-accent-red'}`}>{leg.type.toUpperCase()}</td>
                      <td className="px-3 py-2 text-text-vivid">${leg.strike.toFixed(0)}</td>
                      <td className={`px-3 py-2 font-semibold ${leg.qty > 0 ? 'text-accent-green' : 'text-accent-red'}`}>{leg.qty > 0 ? '+' : ''}{leg.qty}</td>
                      <td className="px-3 py-2 text-text-dim">{(leg.T * 365).toFixed(0)}d</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <Button onClick={execute} variant="primary" className="w-full justify-center">
              ⚡ Execute Strategy (Paper)
            </Button>
          </div>
        )}
      </div>
    </Panel>
  )
}

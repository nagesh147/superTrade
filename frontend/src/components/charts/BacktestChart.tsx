import React, { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { api } from '@/utils/api'
import { Panel, SectionHeader, Button, Select, StatCard } from '@/components/ui'
import type { BacktestResult } from '@/types'
import toast from 'react-hot-toast'

export const BacktestPanel: React.FC = () => {
  const [strategy, setStrategy] = useState('iron_condor')
  const [capital, setCapital] = useState('100000')
  const [result, setResult] = useState<BacktestResult | null>(null)
  const [loading, setLoading] = useState(false)

  const run = async () => {
    setLoading(true)
    try {
      const r = await api.post('/backtest/run', {
        strategy, initial_capital: parseFloat(capital),
        start_date: '2023-01-01', end_date: '2024-01-01'
      })
      setResult(r.data)
      toast.success('Backtest complete!')
    } catch { toast.error('Backtest failed') }
    finally { setLoading(false) }
  }

  const eqData = result?.equity_curve.map((v, i) => ({ i, value: v })) || []
  const pnlData = result?.daily_pnl.map((v, i) => ({ i, pnl: v })) || []

  return (
    <Panel>
      <SectionHeader title="BACKTESTER" subtitle="Historical strategy simulation"/>
      <div className="p-4 space-y-4">
        <div className="flex flex-wrap gap-3">
          <Select value={strategy} onChange={setStrategy} options={[
            {value:'iron_condor',label:'Iron Condor'},
            {value:'straddle',label:'Long Straddle'},
            {value:'butterfly',label:'Butterfly'},
          ]}/>
          <Select value={capital} onChange={setCapital} options={[
            {value:'10000',label:'$10K'},{value:'50000',label:'$50K'},{value:'100000',label:'$100K'},{value:'500000',label:'$500K'}
          ]}/>
          <Button onClick={run} disabled={loading} variant="primary">
            {loading ? '⟳ Running…' : '▶ Run Backtest'}
          </Button>
        </div>

        {result && (
          <div className="animate-slide-up space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <StatCard label="Total Return" value={`${result.total_return_pct > 0 ? '+' : ''}${result.total_return_pct.toFixed(2)}%`}
                positive={result.total_return_pct > 0}/>
              <StatCard label="Sharpe Ratio" value={result.sharpe_ratio.toFixed(3)}
                color={result.sharpe_ratio > 1 ? 'text-accent-green' : result.sharpe_ratio > 0 ? 'text-accent-amber' : 'text-accent-red'}/>
              <StatCard label="Max Drawdown" value={`${result.max_drawdown_pct.toFixed(2)}%`}
                color={result.max_drawdown_pct > -10 ? 'text-accent-green' : 'text-accent-red'}/>
              <StatCard label="Win Rate" value={`${result.win_rate_pct.toFixed(1)}%`}
                color={result.win_rate_pct > 55 ? 'text-accent-green' : 'text-text-base'}/>
              <StatCard label="Ann. Return" value={`${result.annualized_return_pct.toFixed(2)}%`}/>
              <StatCard label="Profit Factor" value={result.profit_factor.toFixed(2)}/>
              <StatCard label="Total Trades" value={result.total_trades.toString()}/>
              <StatCard label="Final Capital" value={`$${result.final_capital.toLocaleString()}`}
                positive={result.final_capital > parseFloat(capital)}/>
            </div>

            <div>
              <p className="text-xs font-mono text-text-muted mb-2 uppercase tracking-wider">Equity Curve</p>
              <ResponsiveContainer width="100%" height={160}>
                <AreaChart data={eqData}>
                  <defs><linearGradient id="eq" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3}/><stop offset="95%" stopColor="#00d4ff" stopOpacity={0}/>
                  </linearGradient></defs>
                  <XAxis dataKey="i" hide/><YAxis domain={['auto','auto']} hide/>
                  <Tooltip formatter={(v: number) => [`$${v.toLocaleString()}`, 'Portfolio']}
                    contentStyle={{ background:'#0a0c12',border:'1px solid #212b42',borderRadius:8,fontFamily:'JetBrains Mono',fontSize:11 }}/>
                  <Area type="monotone" dataKey="value" stroke="#00d4ff" strokeWidth={2} fill="url(#eq)" dot={false}/>
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div>
              <p className="text-xs font-mono text-text-muted mb-2 uppercase tracking-wider">Daily P&L Distribution</p>
              <ResponsiveContainer width="100%" height={100}>
                <BarChart data={pnlData}>
                  <XAxis dataKey="i" hide/><YAxis hide/>
                  <ReferenceLine y={0} stroke="#212b42"/>
                  <Bar dataKey="pnl" radius={[1,1,0,0]}
                    fill="#00ff88" label={false}
                    className="[&>rect]:fill-accent-green [&>rect[value='negative']]:fill-accent-red"/>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </Panel>
  )
}

import React from 'react'
import { ComposedChart, Bar, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { usePnlChart } from '@/hooks/useMarketData'
import { Panel, SectionHeader } from '@/components/ui'

export const PnLChart: React.FC = () => {
  const { data: raw = [] } = usePnlChart(30)
  const pnls = raw.map((d: any) => ({ ...d, pnl: d.value - 100000, pos: Math.max(0, d.value - 100000), neg: Math.min(0, d.value - 100000) }))
  const totalPnl = pnls.length ? pnls[pnls.length-1].pnl : 0

  return (
    <Panel>
      <SectionHeader title="P&L ATTRIBUTION" subtitle="30-day performance"
        right={<span className={`text-sm font-mono font-semibold ${totalPnl >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
          {totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(2)}
        </span>}
      />
      <div className="p-4">
        <ResponsiveContainer width="100%" height={160}>
          <ComposedChart data={pnls} margin={{ top: 5, right: 0, bottom: 0, left: 0 }}>
            <XAxis dataKey="day" hide />
            <YAxis hide domain={['auto','auto']}/>
            <Tooltip formatter={(v: number) => [`$${v.toFixed(2)}`, 'P&L']}
              contentStyle={{ background: '#0a0c12', border: '1px solid #212b42', borderRadius: 8, fontFamily: 'JetBrains Mono' }}/>
            <ReferenceLine y={0} stroke="#212b42" strokeDasharray="3 3"/>
            <Bar dataKey="pos" fill="#00ff8840" radius={[2,2,0,0]}/>
            <Bar dataKey="neg" fill="#ff3d5a40" radius={[0,0,2,2]}/>
            <Line type="monotone" dataKey="pnl" stroke="#00d4ff" strokeWidth={2} dot={false}/>
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  )
}

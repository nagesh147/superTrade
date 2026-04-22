import React from 'react'
import { RadialBarChart, RadialBar, ResponsiveContainer, Cell } from 'recharts'
import { useAppStore } from '@/store'
import { Panel, SectionHeader } from '@/components/ui'

export const VolatilityGauge: React.FC = () => {
  const { ticker } = useAppStore()
  const iv = ticker?.iv || 0
  const ivPct = iv * 100
  const ivRank = Math.min(100, Math.max(0, (iv - 0.30) / (1.50 - 0.30) * 100))
  const color = ivRank > 70 ? '#ff3d5a' : ivRank > 40 ? '#ffb800' : '#00ff88'
  const label = ivRank > 70 ? 'HIGH VOL' : ivRank > 40 ? 'MED VOL' : 'LOW VOL'

  return (
    <Panel>
      <SectionHeader title="IV INDEX" subtitle="Implied volatility gauge"/>
      <div className="p-4 flex flex-col items-center gap-2">
        <div className="relative w-32 h-32">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart cx="50%" cy="50%" innerRadius="70%" outerRadius="100%" startAngle={180} endAngle={0} data={[{value: ivRank}]}>
              <RadialBar background={{ fill: '#1a2035' }} dataKey="value" cornerRadius={4} fill={color}/>
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center mt-4">
            <span className="text-2xl font-mono font-bold text-text-vivid">{ivPct.toFixed(1)}%</span>
            <span className="text-[10px] font-mono" style={{color}}>{label}</span>
          </div>
        </div>
        <div className="w-full grid grid-cols-3 gap-2 text-center">
          {[['30D Low','20%'],['Current',`${ivPct.toFixed(1)}%`],['30D High','120%']].map(([l,v]) => (
            <div key={l}>
              <p className="text-[10px] font-mono text-text-muted">{l}</p>
              <p className="text-xs font-mono text-text-base">{v}</p>
            </div>
          ))}
        </div>
      </div>
    </Panel>
  )
}

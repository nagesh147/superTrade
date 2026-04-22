import React, { useMemo } from 'react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { useAppStore } from '@/store'
import { Panel, SectionHeader } from '@/components/ui'

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="bg-surface-0 border border-border-bright rounded-lg p-3 text-xs font-mono shadow-xl">
      <p className="text-text-vivid text-sm font-semibold">${d.price?.toLocaleString('en-US', { minimumFractionDigits: 2 })}</p>
      <p className="text-text-dim mt-1">IV: {(d.iv * 100).toFixed(1)}%</p>
    </div>
  )
}

export const PriceChart: React.FC = () => {
  const { priceHistory, ticker } = useAppStore()
  const data = priceHistory.slice(-100)
  const prevPrice = data.length > 1 ? data[data.length - 2]?.price : data[0]?.price
  const currentPrice = ticker?.spot || 0
  const isUp = currentPrice >= (prevPrice || 0)

  return (
    <Panel className="flex flex-col" glow>
      <SectionHeader title="CRYPTO/USD SPOT" subtitle="Real-time price feed"
        right={<span className={`text-lg font-mono font-bold ${isUp ? 'text-accent-green' : 'text-accent-red'}`}>
          {isUp ? '▲' : '▼'} ${currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2 })}
        </span>}
      />
      <div className="flex-1 p-4" style={{ minHeight: 180 }}>
        {data.length < 2 ? (
          <div className="h-full flex items-center justify-center text-text-muted text-sm font-mono">
            Waiting for feed<span className="animate-blink ml-1">_</span>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={data} margin={{ top: 5, right: 0, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor={isUp ? '#00ff88' : '#ff3d5a'} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={isUp ? '#00ff88' : '#ff3d5a'} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="time" hide />
              <YAxis domain={['auto','auto']} hide />
              <Tooltip content={<CustomTooltip/>} />
              <Area type="monotone" dataKey="price" stroke={isUp ? '#00ff88' : '#ff3d5a'}
                strokeWidth={2} fill="url(#priceGrad)" dot={false} activeDot={{ r: 4, fill: isUp ? '#00ff88' : '#ff3d5a' }}/>
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </Panel>
  )
}

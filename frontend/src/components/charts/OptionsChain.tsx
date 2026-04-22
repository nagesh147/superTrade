import React, { useState } from 'react'
import { useOptionsChain } from '@/hooks/useMarketData'
import { useAppStore } from '@/store'
import { Panel, SectionHeader, Select, Badge } from '@/components/ui'
import { clsx } from 'clsx'

export const OptionsChain: React.FC = () => {
  const { ticker } = useAppStore()
  const [expiry, setExpiry] = useState('1W')
  const { data, isLoading } = useOptionsChain(expiry)
  const spot = ticker?.spot || data?.spot || 65000
  const chain = data?.chain || []

  const expiries = [
    { value: '1W', label: '1 Week' }, { value: '2W', label: '2 Weeks' },
    { value: '1M', label: '1 Month' }, { value: '3M', label: '3 Months' },
  ]

  return (
    <Panel>
      <SectionHeader title="OPTIONS CHAIN" subtitle={`CRYPTO/USD • Spot: $${spot.toLocaleString()}`}
        right={<Select value={expiry} onChange={setExpiry} options={expiries}/>}
      />
      <div className="overflow-auto">
        {isLoading ? (
          <div className="p-8 text-center text-text-muted font-mono text-sm">Loading chain…</div>
        ) : (
          <table className="w-full text-xs font-mono border-collapse">
            <thead>
              <tr className="border-b border-border-dim">
                <th colSpan={5} className="py-2 text-accent-green text-[10px] uppercase tracking-wider text-center">CALLS</th>
                <th className="py-2 px-4 text-text-muted font-bold text-center border-x border-border-bright">STRIKE</th>
                <th colSpan={5} className="py-2 text-accent-red text-[10px] uppercase tracking-wider text-center">PUTS</th>
              </tr>
              <tr className="border-b border-border-dim text-text-muted text-[10px] uppercase">
                {['Bid','Ask','IV','Δ','OI','Strike','Bid','Ask','IV','Δ','OI'].map((h,i) => (
                  <th key={i} className={clsx('px-2 py-1.5 text-right', i === 5 && 'text-center px-4 border-x border-border-bright font-bold text-text-dim')}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {chain.map((row: any, i: number) => {
                const itm_call = row.strike < spot
                const itm_put  = row.strike > spot
                const atm = Math.abs(row.strike - spot) / spot < 0.015
                return (
                  <tr key={i} className={clsx(
                    'border-b border-border-dim/30 hover:bg-surface-2 transition-colors',
                    atm && 'bg-accent-cyan/5 border-accent-cyan/20'
                  )}>
                    <td className={clsx('px-2 py-1.5 text-right', itm_call ? 'text-accent-green font-semibold' : 'text-text-dim')}>{row.call.bid.toFixed(0)}</td>
                    <td className={clsx('px-2 py-1.5 text-right', itm_call ? 'text-accent-green' : 'text-text-base')}>{row.call.ask.toFixed(0)}</td>
                    <td className="px-2 py-1.5 text-right text-text-dim">{(row.call.iv*100).toFixed(1)}%</td>
                    <td className="px-2 py-1.5 text-right text-accent-green">{row.call.delta.toFixed(2)}</td>
                    <td className="px-2 py-1.5 text-right text-text-muted">{row.call.oi.toFixed(0)}</td>

                    <td className={clsx('px-4 py-1.5 text-center font-mono font-bold border-x border-border-bright',
                      atm ? 'text-accent-cyan text-sm' : 'text-text-vivid'
                    )}>
                      {row.strike.toLocaleString()}
                      {atm && <span className="ml-1 text-[8px] text-accent-cyan">ATM</span>}
                    </td>

                    <td className={clsx('px-2 py-1.5 text-right', itm_put ? 'text-accent-red font-semibold' : 'text-text-dim')}>{row.put.bid.toFixed(0)}</td>
                    <td className={clsx('px-2 py-1.5 text-right', itm_put ? 'text-accent-red' : 'text-text-base')}>{row.put.ask.toFixed(0)}</td>
                    <td className="px-2 py-1.5 text-right text-text-dim">{(row.put.iv*100).toFixed(1)}%</td>
                    <td className="px-2 py-1.5 text-right text-accent-red">{row.put.delta.toFixed(2)}</td>
                    <td className="px-2 py-1.5 text-right text-text-muted">{row.put.oi.toFixed(0)}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </Panel>
  )
}

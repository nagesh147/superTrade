import React from 'react'
import { useAppStore } from '@/store'
import { Panel, SectionHeader } from '@/components/ui'

export const OrderPanel: React.FC = () => {
  const { orders } = useAppStore()
  const statusColor = (s: string) => s === 'filled' ? 'text-accent-green' : s === 'open' ? 'text-accent-cyan' : s === 'cancelled' ? 'text-text-muted' : s === 'rejected' ? 'text-accent-red' : 'text-accent-amber'

  return (
    <Panel>
      <SectionHeader title="ORDER BOOK" subtitle="Recent orders & fills"/>
      <div className="overflow-auto max-h-64">
        <table className="w-full text-xs font-mono">
          <thead>
            <tr className="border-b border-border-dim text-text-muted">
              {['Symbol','Side','Qty','Price','Avg Fill','Status','Fee'].map(h => (
                <th key={h} className="text-left px-3 py-2 uppercase tracking-wider text-[10px]">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 ? (
              <tr><td colSpan={7} className="text-center py-8 text-text-muted">No orders yet</td></tr>
            ) : orders.map((o: any) => (
              <tr key={o.id} className="border-b border-border-dim/50 hover:bg-surface-2 transition-colors">
                <td className="px-3 py-2 text-text-bright">{o.symbol}</td>
                <td className={`px-3 py-2 font-semibold ${o.side === 'buy' ? 'text-accent-green' : 'text-accent-red'}`}>{o.side.toUpperCase()}</td>
                <td className="px-3 py-2 text-text-base">{o.qty}</td>
                <td className="px-3 py-2 text-text-dim">{o.price ? `$${o.price.toFixed(2)}` : 'MKT'}</td>
                <td className="px-3 py-2 text-text-base">{o.avg_price ? `$${o.avg_price.toFixed(2)}` : '-'}</td>
                <td className={`px-3 py-2 font-semibold ${statusColor(o.status)}`}>{o.status.toUpperCase()}</td>
                <td className="px-3 py-2 text-text-muted">${o.commission?.toFixed(4) || '0'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  )
}

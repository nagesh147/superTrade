import React from 'react'
import { PriceChart } from '@/components/dashboard/PriceChart'
import { VolatilityGauge } from '@/components/dashboard/VolatilityGauge'
import { PnLChart } from '@/components/dashboard/PnLChart'
import { RiskPanel } from '@/components/dashboard/RiskPanel'
import { OrderPanel } from '@/components/orders/OrderBook'
import { usePortfolioSummary } from '@/hooks/useMarketData'
import { useAppStore } from '@/store'
import { StatCard, Panel } from '@/components/ui'

export const Dashboard: React.FC = () => {
  const { data: portfolio } = usePortfolioSummary()
  const { ticker } = useAppStore()

  return (
    <div className="space-y-4">
      {/* Top stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatCard label="Portfolio Value" value={`$${(portfolio?.portfolio_value || 100000).toLocaleString()}`}
          color="text-text-vivid"/>
        <StatCard label="Cash Available" value={`$${(portfolio?.cash || 100000).toFixed(0)}`}/>
        <StatCard label="Crypto Spot" value={`$${(ticker?.spot || 0).toLocaleString()}`}
          color="text-accent-cyan"/>
        <StatCard label="IV Index" value={`${((ticker?.iv || 0)*100).toFixed(1)}%`}
          color={(ticker?.iv||0) > 0.8 ? 'text-accent-red' : (ticker?.iv||0) > 0.5 ? 'text-accent-amber' : 'text-accent-green'}/>
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2"><PriceChart/></div>
        <VolatilityGauge/>
      </div>

      {/* P&L + Risk */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <PnLChart/>
        <RiskPanel/>
      </div>

      {/* Orders */}
      <OrderPanel/>
    </div>
  )
}

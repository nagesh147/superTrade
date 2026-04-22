import React, { useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { Navbar } from '@/components/dashboard/Navbar'
import { Dashboard } from '@/pages/Dashboard'
import { ChainPage } from '@/pages/ChainPage'
import { StrategyPage } from '@/pages/StrategyPage'
import { BacktestPage } from '@/pages/BacktestPage'
import { OrdersPage } from '@/pages/OrdersPage'
import { RiskPage } from '@/pages/RiskPage'
import { useAppStore } from '@/store'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useOrders } from '@/hooks/useMarketData'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 2, staleTime: 1000, refetchOnWindowFocus: false } }
})

function AppInner() {
  const { activeTab } = useAppStore()
  useWebSocket()
  
  const pages: Record<string, React.ReactNode> = {
    dashboard: <Dashboard/>,
    chain: <ChainPage/>,
    strategy: <StrategyPage/>,
    backtest: <BacktestPage/>,
    orders: <OrdersPage/>,
    risk: <RiskPage/>,
  }

  return (
    <div className="min-h-screen bg-surface-0 font-body">
      {/* Background atmosphere */}
      <div className="fixed inset-0 bg-radial-glow pointer-events-none"/>
      <div className="fixed inset-0 bg-grid-pattern bg-grid opacity-20 pointer-events-none"/>
      
      <Navbar/>
      <main className="max-w-screen-2xl mx-auto px-4 py-6 animate-fade-in">
        {pages[activeTab] || <Dashboard/>}
      </main>

      <Toaster position="bottom-right" toastOptions={{
        style: { background: '#0e1118', border: '1px solid #212b42', color: '#c5cee0', fontFamily: 'JetBrains Mono', fontSize: 13 }
      }}/>
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppInner/>
    </QueryClientProvider>
  )
}

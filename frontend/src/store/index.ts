import { create } from 'zustand'
import { devtools, subscribeWithSelector } from 'zustand/middleware'
import type { Ticker, PortfolioRisk, Order, WsFeed } from '@/types'

interface AppState {
  // Market Data
  ticker: Ticker | null
  priceHistory: Array<{ time: number; price: number; iv: number }>
  pnlHistory: Array<{ time: number; value: number }>
  wsConnected: boolean
  
  // Portfolio
  risk: PortfolioRisk | null
  cash: number
  portfolioValue: number
  
  // Orders
  orders: Order[]
  
  // UI
  activeTab: string
  selectedStrategy: string
  selectedExpiry: string
  paperMode: boolean
  
  // Actions
  updateTicker: (feed: WsFeed) => void
  setRisk: (risk: PortfolioRisk) => void
  setOrders: (orders: Order[]) => void
  setActiveTab: (tab: string) => void
  setSelectedStrategy: (s: string) => void
  setWsConnected: (v: boolean) => void
  setCash: (v: number) => void
  setPortfolioValue: (v: number) => void
}

export const useAppStore = create<AppState>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      ticker: null,
      priceHistory: [],
      pnlHistory: [],
      wsConnected: false,
      risk: null,
      cash: 100000,
      portfolioValue: 100000,
      orders: [],
      activeTab: 'dashboard',
      selectedStrategy: 'iron_condor',
      selectedExpiry: '1W',
      paperMode: true,

      updateTicker: (feed) => set(state => {
        const now = Date.now()
        const ph = [...state.priceHistory, { time: now, price: feed.spot, iv: feed.iv }].slice(-200)
        const pnl = state.portfolioValue - 100000
        const pp = [...state.pnlHistory, { time: now, value: pnl }].slice(-200)
        return {
          ticker: { spot: feed.spot, bid: feed.bid, ask: feed.ask, iv: feed.iv,
                    volume_24h: feed.volume, open_interest: 0 },
          priceHistory: ph,
          pnlHistory: pp,
        }
      }),
      setRisk: (risk) => set({ risk }),
      setOrders: (orders) => set({ orders }),
      setActiveTab: (activeTab) => set({ activeTab }),
      setSelectedStrategy: (selectedStrategy) => set({ selectedStrategy }),
      setWsConnected: (wsConnected) => set({ wsConnected }),
      setCash: (cash) => set({ cash }),
      setPortfolioValue: (portfolioValue) => set({ portfolioValue }),
    })),
    { name: 'supertrade-store' }
  )
)

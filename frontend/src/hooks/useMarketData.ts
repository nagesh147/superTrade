import { useQuery } from '@tanstack/react-query'
import { api } from '@/utils/api'
import type { OptionChainEntry, PortfolioRisk, BacktestResult, StrategyAnalysis } from '@/types'

export const useOptionsChain = (expiry?: string) =>
  useQuery({ queryKey: ['chain', expiry], queryFn: () => api.get('/market/options-chain', { params: { expiry } }).then(r => r.data), refetchInterval: 5000 })

export const usePortfolioRisk = () =>
  useQuery({ queryKey: ['risk'], queryFn: () => api.get('/portfolio/risk').then(r => r.data as PortfolioRisk), refetchInterval: 2000 })

export const usePortfolioSummary = () =>
  useQuery({ queryKey: ['portfolio'], queryFn: () => api.get('/portfolio/summary').then(r => r.data), refetchInterval: 3000 })

export const useOrders = () =>
  useQuery({ queryKey: ['orders'], queryFn: () => api.get('/orders/').then(r => r.data.orders), refetchInterval: 2000 })

export const useStrategies = () =>
  useQuery({ queryKey: ['strategies'], queryFn: () => api.get('/strategies/list').then(r => r.data.strategies), staleTime: Infinity })

export const useStrategyRecommend = () =>
  useQuery({ queryKey: ['recommend'], queryFn: () => api.get('/strategies/recommend').then(r => r.data), refetchInterval: 10000 })

export const usePnlChart = (days = 30) =>
  useQuery({ queryKey: ['pnl', days], queryFn: () => api.get('/analytics/pnl-chart', { params: { days } }).then(r => r.data.data), refetchInterval: 5000 })

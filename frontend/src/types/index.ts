export interface Ticker {
  spot: number; bid: number; ask: number; iv: number;
  volume_24h: number; open_interest: number;
}

export interface OptionChainEntry {
  strike: number; expiry: string; expiry_T: number;
  call: { bid: number; ask: number; iv: number; delta: number; oi: number };
  put:  { bid: number; ask: number; iv: number; delta: number; oi: number };
}

export interface Order {
  id: string; symbol: string; side: string; qty: number;
  price: number; status: string; filled: number; avg_price: number; commission: number;
}

export interface PortfolioRisk {
  delta: number; gamma: number; vega: number; theta: number;
  var_95: number; var_99: number; sharpe: number; max_drawdown: number;
  risk_level: string; alerts: string[]; leverage: number; daily_pnl: number;
}

export interface BacktestResult {
  total_return_pct: number; annualized_return_pct: number;
  sharpe_ratio: number; sortino_ratio: number; max_drawdown_pct: number;
  win_rate_pct: number; profit_factor: number; total_trades: number;
  total_pnl: number; final_capital: number; var_95: number; calmar_ratio: number;
  equity_curve: number[]; daily_pnl: number[];
}

export interface StrategyAnalysis {
  strategy: string; net_premium: number;
  max_profit: number | string; max_loss: number | string;
  breakevens: number[];
  greeks: { delta: number; gamma: number; vega: number; theta: number };
  rationale: string;
  legs: Array<{ type: string; strike: number; qty: number; T: number }>;
}

export interface WsFeed {
  type: string; spot: number; bid: number; ask: number;
  iv: number; volume: number; timestamp: number;
}

import React, { useState } from 'react'
import { OrderPanel } from '@/components/orders/OrderBook'
import { useOrders } from '@/hooks/useMarketData'
import { useAppStore } from '@/store'
import { Panel, SectionHeader, Button, Select } from '@/components/ui'
import { api } from '@/utils/api'
import toast from 'react-hot-toast'

export const OrdersPage: React.FC = () => {
  const { data: orders = [] } = useOrders()
  const { setOrders, ticker } = useAppStore()
  const [symbol, setSymbol] = useState('BTC-PERP')
  const [side, setSide] = useState('buy')
  const [qty, setQty] = useState('0.01')
  const [price, setPrice] = useState('')
  const [type, setType] = useState('market')

  React.useEffect(() => { setOrders(orders) }, [orders])

  const submit = async () => {
    try {
      await api.post('/orders/create', {
        symbol, side, order_type: type, quantity: parseFloat(qty),
        price: price ? parseFloat(price) : undefined
      })
      toast.success(`${side.toUpperCase()} order submitted`)
    } catch { toast.error('Order failed') }
  }

  return (
    <div className="space-y-4">
      <Panel>
        <SectionHeader title="PLACE ORDER" subtitle="Manual order entry"/>
        <div className="p-4 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <Select value={symbol} onChange={setSymbol} options={[
            {value:'BTC-PERP',label:'BTC-PERP'},{value:'ETH-PERP',label:'ETH-PERP'},
            {value:'BTC-CALL',label:'BTC-CALL'},{value:'BTC-PUT',label:'BTC-PUT'},
          ]}/>
          <Select value={side} onChange={setSide} options={[{value:'buy',label:'BUY'},{value:'sell',label:'SELL'}]}/>
          <Select value={type} onChange={setType} options={[{value:'market',label:'MARKET'},{value:'limit',label:'LIMIT'}]}/>
          <input value={qty} onChange={e=>setQty(e.target.value)} placeholder="Quantity"
            className="bg-surface-2 border border-border-base text-text-base rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:border-accent-cyan"/>
          <input value={price} onChange={e=>setPrice(e.target.value)} placeholder={`Price (${type==='market'?'market':ticker?.spot?.toFixed(0)||'auto'})`}
            disabled={type==='market'}
            className="bg-surface-2 border border-border-base text-text-base rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:border-accent-cyan disabled:opacity-40"/>
          <Button onClick={submit} variant={side==='buy'?'primary':'danger'} className="w-full justify-center">
            {side.toUpperCase()} {symbol}
          </Button>
        </div>
      </Panel>
      <OrderPanel/>
    </div>
  )
}

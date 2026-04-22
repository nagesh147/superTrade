import { useEffect, useRef, useCallback } from 'react'
import { useAppStore } from '@/store'
import { WS_URL } from '@/utils/api'

export function useWebSocket() {
  const ws = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<number>()
  const { updateTicker, setWsConnected } = useAppStore()

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(WS_URL)
      ws.current.onopen = () => { setWsConnected(true); console.log('WS connected') }
      ws.current.onmessage = (e) => {
        try { const d = JSON.parse(e.data); if (d.type === 'ticker') updateTicker(d) }
        catch {}
      }
      ws.current.onclose = () => {
        setWsConnected(false)
        reconnectTimer.current = window.setTimeout(connect, 3000)
      }
      ws.current.onerror = () => ws.current?.close()
    } catch (e) { console.error('WS error:', e) }
  }, [updateTicker, setWsConnected])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimer.current)
      ws.current?.close()
    }
  }, [connect])
}

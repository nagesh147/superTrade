import React from 'react'
import { clsx } from 'clsx'

// ── Panel ──────────────────────────────────────────────────────────────────
export const Panel: React.FC<{ children: React.ReactNode; className?: string; glow?: boolean }> = ({ children, className, glow }) => (
  <div className={clsx(
    'rounded-xl border border-border-base bg-surface-1 backdrop-blur-sm relative overflow-hidden',
    glow && 'border-accent-cyan/30 shadow-[0_0_30px_rgba(0,212,255,0.06)]',
    className
  )}>
    <div className="absolute inset-0 bg-grid-pattern bg-grid opacity-30 pointer-events-none"/>
    {children}
  </div>
)

// ── Badge ──────────────────────────────────────────────────────────────────
export const Badge: React.FC<{ label: string; color?: 'green'|'red'|'amber'|'cyan'|'dim'; dot?: boolean }> = ({ label, color='dim', dot=true }) => {
  const colors = {
    green: 'text-accent-green border-accent-green/30 bg-accent-green/10',
    red:   'text-accent-red   border-accent-red/30   bg-accent-red/10',
    amber: 'text-accent-amber border-accent-amber/30 bg-accent-amber/10',
    cyan:  'text-accent-cyan  border-accent-cyan/30  bg-accent-cyan/10',
    dim:   'text-text-dim     border-border-base      bg-surface-2',
  }
  const dotColors = { green:'bg-accent-green', red:'bg-accent-red', amber:'bg-accent-amber', cyan:'bg-accent-cyan', dim:'bg-text-dim' }
  return (
    <span className={clsx('inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md border text-xs font-mono font-medium', colors[color])}>
      {dot && <span className={clsx('w-1.5 h-1.5 rounded-full animate-pulse-slow', dotColors[color])}/>}
      {label}
    </span>
  )
}

// ── Stat Card ──────────────────────────────────────────────────────────────
export const StatCard: React.FC<{ label: string; value: string; change?: string; positive?: boolean; sub?: string; color?: string }> = ({ label, value, change, positive, sub, color }) => (
  <div className="flex flex-col gap-1 p-4 rounded-lg border border-border-base bg-surface-2 hover:border-border-bright transition-colors">
    <p className="text-xs font-mono text-text-muted uppercase tracking-widest">{label}</p>
    <p className={clsx('text-2xl font-mono font-semibold', color || 'text-text-vivid')}>{value}</p>
    {(change || sub) && (
      <p className={clsx('text-xs font-mono', positive === undefined ? 'text-text-dim' : positive ? 'text-accent-green' : 'text-accent-red')}>
        {change && (positive ? '▲ ' : '▼ ')}{change || sub}
      </p>
    )}
  </div>
)

// ── Greek Pill ──────────────────────────────────────────────────────────────
export const GreekPill: React.FC<{ name: string; value: number; unit?: string; thresholds?: [number,number] }> = ({ name, value, unit='', thresholds }) => {
  const abs = Math.abs(value)
  const warn = thresholds ? abs > thresholds[1] ? 'text-accent-red' : abs > thresholds[0] ? 'text-accent-amber' : 'text-text-base' : 'text-text-base'
  return (
    <div className="flex flex-col items-center gap-0.5 px-3 py-2 rounded-lg border border-border-base bg-surface-2">
      <span className="text-[10px] font-mono text-text-muted uppercase tracking-wider">{name}</span>
      <span className={clsx('text-sm font-mono font-semibold', warn)}>{value > 0 ? '+' : ''}{value.toFixed(4)}{unit}</span>
    </div>
  )
}

// ── Button ──────────────────────────────────────────────────────────────────
export const Button: React.FC<{ children: React.ReactNode; onClick?: () => void; variant?: 'primary'|'danger'|'ghost'|'outline'; size?: 'sm'|'md'|'lg'; disabled?: boolean; className?: string }> = ({ children, onClick, variant='outline', size='md', disabled, className }) => {
  const variants = {
    primary: 'bg-accent-cyan text-surface-0 hover:bg-accent-cyan/80 border-accent-cyan',
    danger:  'bg-accent-red/20 text-accent-red hover:bg-accent-red/30 border-accent-red/50',
    ghost:   'bg-transparent text-text-dim hover:text-text-base hover:bg-surface-3 border-transparent',
    outline: 'bg-transparent text-text-base hover:text-text-vivid hover:bg-surface-3 border-border-base hover:border-border-bright',
  }
  const sizes = { sm: 'px-3 py-1.5 text-xs', md: 'px-4 py-2 text-sm', lg: 'px-6 py-3 text-base' }
  return (
    <button onClick={onClick} disabled={disabled}
      className={clsx('inline-flex items-center gap-2 font-mono font-medium rounded-lg border transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed', variants[variant], sizes[size], className)}>
      {children}
    </button>
  )
}

// ── Select ──────────────────────────────────────────────────────────────────
export const Select: React.FC<{ value: string; onChange: (v: string) => void; options: {value:string;label:string}[]; className?: string }> = ({ value, onChange, options, className }) => (
  <select value={value} onChange={e => onChange(e.target.value)}
    className={clsx('bg-surface-2 border border-border-base text-text-base rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:border-accent-cyan transition-colors', className)}>
    {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
  </select>
)

// ── Section Header ──────────────────────────────────────────────────────────
export const SectionHeader: React.FC<{ title: string; subtitle?: string; right?: React.ReactNode }> = ({ title, subtitle, right }) => (
  <div className="flex items-center justify-between p-4 border-b border-border-dim">
    <div>
      <h3 className="text-sm font-display font-semibold text-text-vivid tracking-wide">{title}</h3>
      {subtitle && <p className="text-xs text-text-muted mt-0.5">{subtitle}</p>}
    </div>
    {right && <div className="flex items-center gap-2">{right}</div>}
  </div>
)

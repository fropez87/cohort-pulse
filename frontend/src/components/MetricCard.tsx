import { useEffect, useState } from 'react'
import { Card } from './ui/card'
import { cn } from '../lib/utils'
import type { LucideIcon } from 'lucide-react'

interface MetricCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  trend?: {
    value: number
    label: string
  }
  delay?: number
  format?: 'number' | 'currency' | 'percent'
}

export function MetricCard({ title, value, icon: Icon, trend, delay = 0, format }: MetricCardProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [displayValue, setDisplayValue] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay)
    return () => clearTimeout(timer)
  }, [delay])

  // Animated counter for numbers
  useEffect(() => {
    if (!isVisible || typeof value !== 'number') return

    const duration = 1000
    const steps = 30
    const stepValue = value / steps
    let current = 0

    const interval = setInterval(() => {
      current += stepValue
      if (current >= value) {
        setDisplayValue(value)
        clearInterval(interval)
      } else {
        setDisplayValue(Math.floor(current))
      }
    }, duration / steps)

    return () => clearInterval(interval)
  }, [isVisible, value])

  const formatValue = (val: number) => {
    if (format === 'currency') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(val)
    }
    if (format === 'percent') {
      return `${val.toFixed(1)}%`
    }
    return new Intl.NumberFormat('en-US').format(val)
  }

  return (
    <Card className={cn(
      "overflow-hidden opacity-0 border border-border shadow-sm hover:shadow-md transition-shadow duration-150",
      isVisible && "animate-fade-in"
    )}>
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">
              {title}
            </p>
            <p className="text-2xl font-semibold tracking-tight text-foreground">
              {typeof value === 'number' ? formatValue(displayValue) : value}
            </p>
            {trend && (
              <p className={cn(
                "text-sm font-medium flex items-center gap-1",
                trend.value >= 0 ? "text-emerald-600" : "text-red-500"
              )}>
                <span>{trend.value >= 0 ? '↑' : '↓'}</span>
                <span>{Math.abs(trend.value)}% {trend.label}</span>
              </p>
            )}
          </div>
          <div className="p-2.5 rounded-lg bg-muted">
            <Icon className="h-5 w-5 text-muted-foreground" />
          </div>
        </div>
      </div>
    </Card>
  )
}

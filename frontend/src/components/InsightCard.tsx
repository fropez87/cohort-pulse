import { cn } from '../lib/utils'
import { TrendingUp, TrendingDown, Info } from 'lucide-react'

interface InsightCardProps {
  type: 'positive' | 'warning' | 'info'
  title: string
  text: string
  delay?: number
}

export function InsightCard({ type, title, text, delay = 0 }: InsightCardProps) {
  const config = {
    positive: {
      icon: TrendingUp,
      bg: 'bg-emerald-50',
      border: 'border-l-emerald-500',
      iconColor: 'text-emerald-500',
    },
    warning: {
      icon: TrendingDown,
      bg: 'bg-amber-50',
      border: 'border-l-amber-500',
      iconColor: 'text-amber-500',
    },
    info: {
      icon: Info,
      bg: 'bg-primary/5',
      border: 'border-l-primary',
      iconColor: 'text-primary',
    },
  }

  const { icon: Icon, bg, border, iconColor } = config[type]

  return (
    <div
      className={cn(
        "p-4 rounded-lg border-l-4 transition-all duration-300 hover:translate-x-1 opacity-0 animate-fade-in",
        bg,
        border
      )}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start gap-3">
        <div className={cn("mt-0.5", iconColor)}>
          <Icon className="h-5 w-5" />
        </div>
        <div className="space-y-1">
          <p className="font-semibold text-foreground">{title}</p>
          <p className="text-sm text-muted-foreground">{text}</p>
        </div>
      </div>
    </div>
  )
}

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
      iconColor: 'text-emerald-600',
    },
    warning: {
      icon: TrendingDown,
      bg: 'bg-amber-50',
      border: 'border-l-amber-500',
      iconColor: 'text-amber-600',
    },
    info: {
      icon: Info,
      bg: 'bg-muted',
      border: 'border-l-muted-foreground',
      iconColor: 'text-muted-foreground',
    },
  }

  const { icon: Icon, bg, border, iconColor } = config[type]

  return (
    <div
      className={cn(
        "p-4 rounded-md border-l-4 opacity-0 animate-fade-in",
        bg,
        border
      )}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start gap-3">
        <div className={cn("mt-0.5", iconColor)}>
          <Icon className="h-4 w-4" />
        </div>
        <div className="space-y-0.5">
          <p className="font-medium text-sm text-foreground">{title}</p>
          <p className="text-sm text-muted-foreground">{text}</p>
        </div>
      </div>
    </div>
  )
}

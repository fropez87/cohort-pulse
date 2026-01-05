import { useMemo } from 'react'
import { cn } from '../lib/utils'

interface CohortHeatmapProps {
  data: Record<string, Record<string, number | null>>
  type: 'retention' | 'revenue' | 'customers' | 'revenue_retention'
}

export function CohortHeatmap({ data, type }: CohortHeatmapProps) {
  const { rows, columns, maxValue } = useMemo(() => {
    const rowKeys = Object.keys(data).sort()
    const colSet = new Set<string>()
    let max = 0

    rowKeys.forEach(row => {
      Object.keys(data[row]).forEach(col => {
        colSet.add(col)
        const val = data[row][col]
        if (val !== null && val !== undefined) {
          max = Math.max(max, val)
        }
      })
    })

    const colKeys = Array.from(colSet).sort((a, b) => {
      const numA = parseInt(a.replace(/\D/g, ''))
      const numB = parseInt(b.replace(/\D/g, ''))
      return numA - numB
    })

    return { rows: rowKeys, columns: colKeys, maxValue: max }
  }, [data])

  const getCellStyle = (value: number | null | undefined) => {
    if (value === null || value === undefined) {
      return { backgroundColor: 'rgba(0,0,0,0.05)' }
    }

    if (type === 'retention' || type === 'revenue_retention') {
      const ratio = Math.min(value / 100, 1)
      // Interpolate from red through yellow to green
      const r = ratio < 0.5 ? 255 : Math.floor(255 * (1 - (ratio - 0.5) * 2))
      const g = ratio < 0.5 ? Math.floor(255 * ratio * 2) : 255
      const b = 0
      return { backgroundColor: `rgba(${r}, ${g}, ${b}, 0.7)` }
    }

    if (type === 'revenue') {
      const ratio = maxValue > 0 ? Math.min(value / maxValue, 1) : 0
      return { backgroundColor: `rgba(59, 130, 246, ${0.1 + ratio * 0.7})` }
    }

    // Customers
    const ratio = maxValue > 0 ? Math.min(value / maxValue, 1) : 0
    return { backgroundColor: `rgba(124, 58, 237, ${0.1 + ratio * 0.7})` }
  }

  const formatValue = (value: number | null | undefined) => {
    if (value === null || value === undefined) return '-'

    if (type === 'retention' || type === 'revenue_retention') {
      return `${value.toFixed(1)}%`
    }

    if (type === 'revenue') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
        notation: value >= 10000 ? 'compact' : 'standard',
      }).format(value)
    }

    return new Intl.NumberFormat('en-US').format(value)
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="sticky left-0 z-10 bg-background p-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wide border-b">
              Cohort
            </th>
            {columns.map(col => (
              <th
                key={col}
                className="p-3 text-center text-xs font-semibold text-muted-foreground uppercase tracking-wide border-b whitespace-nowrap"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr
              key={row}
              className="opacity-0 animate-fade-in"
              style={{ animationDelay: `${rowIndex * 50}ms` }}
            >
              <td className="sticky left-0 z-10 bg-background p-3 text-sm font-medium text-foreground border-b whitespace-nowrap">
                {row}
              </td>
              {columns.map(col => {
                const value = data[row]?.[col]
                return (
                  <td
                    key={col}
                    className={cn(
                      "p-3 text-center text-sm font-medium border-b transition-all duration-200 hover:ring-2 hover:ring-primary hover:ring-inset cursor-default",
                      value !== null && value !== undefined ? "text-foreground" : "text-muted-foreground"
                    )}
                    style={getCellStyle(value)}
                    title={`${row} - ${col}: ${formatValue(value)}`}
                  >
                    {formatValue(value)}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

import { useMemo } from 'react'
import { cn } from '../lib/utils'

interface CohortHeatmapProps {
  data: Record<string, Record<string, number | null>>
  type: 'retention' | 'revenue' | 'customers' | 'revenue_retention'
}

// Teal accent color matching our design system
const ACCENT_COLOR = { r: 42, g: 157, b: 143 } // #2a9d8f

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
      return { backgroundColor: '#f5f5f5' }
    }

    if (type === 'retention' || type === 'revenue_retention') {
      // Subtle green scale for retention
      const ratio = Math.min(value / 100, 1)
      const opacity = 0.15 + ratio * 0.5
      return { backgroundColor: `rgba(${ACCENT_COLOR.r}, ${ACCENT_COLOR.g}, ${ACCENT_COLOR.b}, ${opacity})` }
    }

    if (type === 'revenue') {
      // Blue scale for revenue
      const ratio = maxValue > 0 ? Math.min(value / maxValue, 1) : 0
      return { backgroundColor: `rgba(59, 130, 246, ${0.1 + ratio * 0.5})` }
    }

    // Customers - use accent teal
    const ratio = maxValue > 0 ? Math.min(value / maxValue, 1) : 0
    return { backgroundColor: `rgba(${ACCENT_COLOR.r}, ${ACCENT_COLOR.g}, ${ACCENT_COLOR.b}, ${0.1 + ratio * 0.5})` }
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
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr>
            <th className="sticky left-0 z-10 bg-muted p-3 text-left text-xs font-medium text-muted-foreground border-b border-border">
              Cohort
            </th>
            {columns.map(col => (
              <th
                key={col}
                className="p-3 text-center text-xs font-medium text-muted-foreground border-b border-border bg-muted whitespace-nowrap"
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
              style={{ animationDelay: `${rowIndex * 30}ms` }}
            >
              <td className="sticky left-0 z-10 bg-white p-3 text-sm font-medium text-foreground border-b border-border whitespace-nowrap">
                {row}
              </td>
              {columns.map(col => {
                const value = data[row]?.[col]
                return (
                  <td
                    key={col}
                    className={cn(
                      "p-3 text-center text-sm border-b border-border transition-colors duration-150",
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

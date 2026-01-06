import { cn } from '../lib/utils'
import type { CohortMatrixData } from '../types'

interface PayerMatrixProps {
  data: CohortMatrixData
}

export function PayerMatrix({ data }: PayerMatrixProps) {
  const { matrix, payment_months, totals } = data

  const formatCurrency = (value: number) => {
    if (Math.abs(value) < 0.5) return ''
    if (value < 0) {
      return `(${Math.abs(Math.round(value)).toLocaleString()})`
    }
    return Math.round(value).toLocaleString()
  }

  const getCellStyle = (value: number) => {
    if (Math.abs(value) < 0.5) return {}
    if (value < 0) {
      return { color: '#dc2626' } // red for negative
    }
    return {}
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm font-mono">
        <thead>
          <tr className="bg-muted">
            <th className="sticky left-0 z-10 bg-muted p-3 text-left text-xs font-semibold text-foreground border-b border-r border-border whitespace-nowrap">
              DOS Month
            </th>
            <th className="p-3 text-right text-xs font-semibold text-foreground border-b border-r border-border whitespace-nowrap bg-blue-50">
              Gross Charge
            </th>
            {payment_months.map(month => (
              <th
                key={month}
                className="p-3 text-right text-xs font-semibold text-foreground border-b border-border whitespace-nowrap"
              >
                {month}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, rowIndex) => (
            <tr
              key={row.dos_month}
              className={cn(
                "hover:bg-muted/50 transition-colors",
                rowIndex % 2 === 0 ? "bg-white" : "bg-gray-50/50"
              )}
            >
              <td className="sticky left-0 z-10 p-3 text-sm font-medium text-foreground border-b border-r border-border whitespace-nowrap bg-inherit">
                {row.dos_month}
              </td>
              <td className="p-3 text-right text-sm border-b border-r border-border whitespace-nowrap bg-blue-50/50 font-semibold">
                {formatCurrency(row.gross_charge)}
              </td>
              {payment_months.map(month => {
                const value = row.payments[month] || 0
                return (
                  <td
                    key={month}
                    className="p-3 text-right text-sm border-b border-border whitespace-nowrap"
                    style={getCellStyle(value)}
                  >
                    {formatCurrency(value)}
                  </td>
                )
              })}
            </tr>
          ))}
          {/* Grand Totals Row */}
          <tr className="bg-muted font-bold border-t-2 border-foreground">
            <td className="sticky left-0 z-10 bg-muted p-3 text-sm font-bold text-foreground border-r border-border whitespace-nowrap">
              Grand Totals
            </td>
            <td className="p-3 text-right text-sm border-r border-border whitespace-nowrap bg-blue-100">
              {formatCurrency(totals.gross_charge)}
            </td>
            {payment_months.map(month => {
              const value = totals.payments[month] || 0
              return (
                <td
                  key={month}
                  className="p-3 text-right text-sm border-border whitespace-nowrap"
                  style={getCellStyle(value)}
                >
                  {formatCurrency(value)}
                </td>
              )
            })}
          </tr>
        </tbody>
      </table>
    </div>
  )
}

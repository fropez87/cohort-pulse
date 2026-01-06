import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { RetentionCurve, CohortSizeChart } from './Charts'
import type { RetentionAnalysisResponse } from '../types'
import { RefreshCw, Download } from 'lucide-react'
import { useState } from 'react'

interface RetentionDashboardProps {
  data: RetentionAnalysisResponse
  onReset: () => void
}

type TableType = 'retention' | 'customers' | 'revenue_retention' | 'revenue'

export function RetentionDashboard({ data, onReset }: RetentionDashboardProps) {
  const [activeTable, setActiveTable] = useState<TableType>('retention')

  const { summary, metrics, insights, retention_table, revenue_table, customer_table, revenue_retention_table, retention_curve, cohort_sizes } = data

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  const formatPercent = (value: number) => {
    return `${value.toFixed(1)}%`
  }

  const getTableData = () => {
    switch (activeTable) {
      case 'retention':
        return { table: retention_table, title: 'Customer Retention %', format: 'percent' }
      case 'customers':
        return { table: customer_table, title: 'Customer Count', format: 'number' }
      case 'revenue_retention':
        return { table: revenue_retention_table, title: 'Revenue Retention %', format: 'percent' }
      case 'revenue':
        return { table: revenue_table, title: 'Revenue $', format: 'currency' }
      default:
        return { table: retention_table, title: 'Customer Retention %', format: 'percent' }
    }
  }

  const { table: currentTable, format: tableFormat } = getTableData()

  const renderTableValue = (value: number | undefined) => {
    if (value === undefined || value === null) return ''
    switch (tableFormat) {
      case 'percent':
        return formatPercent(value)
      case 'currency':
        return formatCurrency(value)
      default:
        return value.toLocaleString()
    }
  }

  const getCellColor = (value: number | undefined, format: string) => {
    if (value === undefined || value === null) return ''
    if (format === 'percent') {
      if (value >= 50) return 'bg-primary/20'
      if (value >= 30) return 'bg-primary/10'
      if (value >= 15) return 'bg-primary/5'
    }
    return ''
  }

  // Get column headers from the first row of data
  const getColumns = () => {
    if (!currentTable) return []
    const firstRow = Object.values(currentTable)[0] as Record<string, number> | undefined
    if (!firstRow) return []
    return Object.keys(firstRow).sort((a, b) => parseInt(a) - parseInt(b))
  }

  const columns = getColumns()
  const cohorts = currentTable ? Object.keys(currentTable).sort() : []

  // Export to CSV function
  const handleExportCSV = () => {
    if (!retention_table) return

    // Build CSV with all tables
    const rows: string[] = []

    // Retention Table
    rows.push('Customer Retention %')
    const retCohorts = Object.keys(retention_table).sort()
    const retCols = Object.keys(Object.values(retention_table)[0] || {}).sort((a, b) => parseInt(a) - parseInt(b))
    rows.push(['Cohort', ...retCols.map(c => `Month ${c}`)].join(','))
    retCohorts.forEach(cohort => {
      const rowData = retention_table[cohort] as Record<string, number>
      rows.push([cohort, ...retCols.map(c => rowData[c]?.toFixed(1) || '')].join(','))
    })
    rows.push('')

    // Revenue Table
    if (revenue_table) {
      rows.push('Revenue $')
      const revCohorts = Object.keys(revenue_table).sort()
      const revCols = Object.keys(Object.values(revenue_table)[0] || {}).sort((a, b) => parseInt(a) - parseInt(b))
      rows.push(['Cohort', ...revCols.map(c => `Month ${c}`)].join(','))
      revCohorts.forEach(cohort => {
        const rowData = revenue_table[cohort] as Record<string, number>
        rows.push([cohort, ...revCols.map(c => rowData[c]?.toFixed(2) || '')].join(','))
      })
    }

    const csv = rows.join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'cohort_analysis.csv'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  return (
    <div className="space-y-6">
      {/* Header with actions */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Retention Analytics</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {summary?.unique_customers?.toLocaleString()} customers across {summary?.total_orders?.toLocaleString()} orders
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleExportCSV}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 text-foreground text-sm font-medium transition-colors"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </button>
          <button
            onClick={onReset}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-medium transition-all duration-150 shadow-sm hover:shadow"
          >
            <RefreshCw className="h-4 w-4" />
            New File
          </button>
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Total Orders</p>
            <p className="text-2xl font-bold text-foreground mt-1">{summary?.total_orders?.toLocaleString()}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Unique Customers</p>
            <p className="text-2xl font-bold text-foreground mt-1">{summary?.unique_customers?.toLocaleString()}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Total Revenue</p>
            <p className="text-2xl font-bold text-foreground mt-1">{formatCurrency(summary?.total_revenue || 0)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Avg Order Value</p>
            <p className="text-2xl font-bold text-foreground mt-1">{formatCurrency(metrics?.aov || 0)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Customer LTV</p>
            <p className="text-2xl font-bold text-foreground mt-1">{formatCurrency(metrics?.ltv || 0)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Repeat Rate</p>
            <p className="text-2xl font-bold text-foreground mt-1">{formatPercent(metrics?.repeat_rate || 0)}</p>
          </CardContent>
        </Card>
      </div>

      {/* Date Range */}
      {summary?.date_range && (
        <p className="text-sm text-muted-foreground">{summary.date_range}</p>
      )}

      {/* Charts */}
      {(retention_curve || cohort_sizes) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {retention_curve && retention_curve.length > 0 && (
            <RetentionCurve data={retention_curve} />
          )}
          {cohort_sizes && cohort_sizes.length > 0 && (
            <CohortSizeChart data={cohort_sizes} />
          )}
        </div>
      )}

      {/* Insights - 2 columns x 3 rows grid */}
      {insights && insights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Key Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {insights.slice(0, 6).map((insight, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-l-4 ${
                    insight.type === 'positive' ? 'border-l-green-500 bg-green-50' :
                    insight.type === 'warning' ? 'border-l-yellow-500 bg-yellow-50' :
                    'border-l-primary bg-primary/5'
                  }`}
                >
                  <p className="font-semibold text-foreground">{insight.title}</p>
                  <p className="text-sm text-muted-foreground mt-1">{insight.text}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Cohort Tables */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Cohort Tables</CardTitle>
            <div className="flex gap-1 p-1 rounded-lg bg-muted">
              {[
                { key: 'retention', label: 'Retention %' },
                { key: 'customers', label: 'Customers' },
                { key: 'revenue_retention', label: 'Rev Retention %' },
                { key: 'revenue', label: 'Revenue $' },
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTable(tab.key as TableType)}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    activeTable === tab.key
                      ? 'bg-white text-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/50">
                  <th className="text-left py-2 px-3 font-semibold text-foreground sticky left-0 bg-muted/50">Cohort</th>
                  {columns.map((col) => (
                    <th key={col} className="text-right py-2 px-3 font-semibold text-foreground min-w-[80px]">
                      Month {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {cohorts.map((cohort, rowIndex) => {
                  const rowData = currentTable?.[cohort] as Record<string, number> | undefined
                  return (
                    <tr key={cohort} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'}>
                      <td className="py-2 px-3 font-medium sticky left-0 bg-inherit">{cohort}</td>
                      {columns.map((col) => {
                        const value = rowData?.[col]
                        return (
                          <td
                            key={col}
                            className={`py-2 px-3 text-right ${getCellColor(value, tableFormat)}`}
                          >
                            {renderTableValue(value)}
                          </td>
                        )
                      })}
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Footer */}
      <div className="border-t border-border pt-8 mt-8">
        <p className="text-sm text-muted-foreground text-center">
          Your data is processed locally and is not stored on our servers.
        </p>
      </div>
    </div>
  )
}

import { useState, useCallback } from 'react'
import { Header } from './components/Header'
import { LandingPage, type AnalysisType } from './components/LandingPage'
import { PayerMatrix } from './components/CohortHeatmap'
import { RetentionDashboard } from './components/RetentionDashboard'
import { DashboardSkeleton } from './components/LoadingState'
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card'
import type { UploadResponse, CohortMatrixData, FiltersData, RetentionAnalysisResponse } from './types'
import { Download, RefreshCw } from 'lucide-react'

const API_URL = '/api'

function App() {
  // Common state
  const [analysisType, setAnalysisType] = useState<AnalysisType | null>(null)
  const [isUploaded, setIsUploaded] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Waterfall state
  const [matrixData, setMatrixData] = useState<CohortMatrixData | null>(null)
  const [filters, setFilters] = useState<FiltersData>({ payers: [], service_types: [] })
  const [selectedPayer, setSelectedPayer] = useState<string>('')
  const [selectedServiceType, setSelectedServiceType] = useState<string>('')
  const [rowCount, setRowCount] = useState(0)
  const [rawData, setRawData] = useState<Array<Record<string, unknown>>>([])

  // Retention state
  const [retentionData, setRetentionData] = useState<RetentionAnalysisResponse | null>(null)

  const handleFileSelect = async (file: File, type: AnalysisType) => {
    setIsLoading(true)
    setError(null)
    setAnalysisType(type)

    try {
      const formData = new FormData()
      formData.append('file', file)

      if (type === 'waterfall') {
        // Waterfall upload - now returns matrix data directly
        const response = await fetch(`${API_URL}/upload`, {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          throw new Error('Upload failed')
        }

        const result: UploadResponse = await response.json()
        setFilters(result.filters)
        setRowCount(result.rows)

        // Store raw data for client-side filtering
        if (result.data) {
          setRawData(result.data)
        }

        // Use matrix data from response (for serverless compatibility)
        if (result.matrix && result.payment_months && result.totals) {
          setMatrixData({
            matrix: result.matrix,
            payment_months: result.payment_months,
            totals: result.totals
          })
        } else {
          // Fallback to fetching matrix (for local dev with stateful backend)
          await fetchMatrix()
        }

        setIsUploaded(true)
      } else {
        // Retention upload
        const response = await fetch(`${API_URL}/analyze`, {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          throw new Error('Analysis failed')
        }

        const result: RetentionAnalysisResponse = await response.json()
        if (!result.success) {
          throw new Error(result.error || 'Analysis failed')
        }
        setRetentionData(result)
        setIsUploaded(true)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchMatrix = useCallback(async (payer?: string, serviceType?: string) => {
    // If we have raw data, use POST to cohort-matrix with data
    if (rawData.length > 0) {
      setIsLoading(true)
      try {
        const response = await fetch(`${API_URL}/cohort-matrix`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            data: rawData,
            payer: payer || null,
            service_type: serviceType || null
          })
        })
        if (!response.ok) {
          throw new Error('Failed to fetch matrix')
        }
        const data: CohortMatrixData = await response.json()
        setMatrixData(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load matrix')
      } finally {
        setIsLoading(false)
      }
    } else {
      // Fallback to GET (for local dev)
      setIsLoading(true)
      try {
        const params = new URLSearchParams()
        if (payer) params.append('payer', payer)
        if (serviceType) params.append('service_type', serviceType)

        const response = await fetch(`${API_URL}/cohort-matrix?${params}`)
        if (!response.ok) {
          throw new Error('Failed to fetch matrix')
        }

        const data: CohortMatrixData = await response.json()
        setMatrixData(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load matrix')
      } finally {
        setIsLoading(false)
      }
    }
  }, [rawData])

  // Only refetch when filters change (not on initial load - that uses upload response)
  const handleFilterChange = useCallback((payer: string, serviceType: string) => {
    if (isUploaded && analysisType === 'waterfall') {
      fetchMatrix(payer || undefined, serviceType || undefined)
    }
  }, [isUploaded, analysisType, fetchMatrix])

  const handleReset = () => {
    setAnalysisType(null)
    setIsUploaded(false)
    setMatrixData(null)
    setRetentionData(null)
    setFilters({ payers: [], service_types: [] })
    setSelectedPayer('')
    setSelectedServiceType('')
    setError(null)
    setRowCount(0)
    setRawData([])
  }

  const handleExportCSV = () => {
    if (!matrixData) return

    const { matrix, payment_months, totals } = matrixData

    // Build CSV header
    const headers = ['DOS Month', 'Gross Charge', ...payment_months]
    const rows = [headers.join(',')]

    // Add data rows
    matrix.forEach(row => {
      const values = [
        row.dos_month,
        row.gross_charge,
        ...payment_months.map(m => row.payments[m] || 0)
      ]
      rows.push(values.join(','))
    })

    // Add totals row
    const totalValues = [
      'Grand Totals',
      totals.gross_charge,
      ...payment_months.map(m => totals.payments[m] || 0)
    ]
    rows.push(totalValues.join(','))

    const csv = rows.join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'payer_waterfall.csv'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  return (
    <div className="min-h-screen bg-gradient-subtle">
      <Header onLogoClick={handleReset} />

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Landing Page */}
        {!isUploaded && !isLoading && (
          <LandingPage
            onFileSelect={handleFileSelect}
            isLoading={isLoading}
            error={error}
          />
        )}

        {/* Loading State */}
        {isLoading && !isUploaded && <DashboardSkeleton />}

        {/* Retention Dashboard */}
        {isUploaded && analysisType === 'retention' && retentionData && (
          <RetentionDashboard data={retentionData} onReset={handleReset} />
        )}

        {/* Waterfall Dashboard */}
        {isUploaded && analysisType === 'waterfall' && (
          <div className="space-y-6">
            {/* Header with actions */}
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-foreground">Payer Waterfall</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  {rowCount.toLocaleString()} payment records loaded
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleExportCSV}
                  disabled={!matrixData}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 text-foreground text-sm font-medium transition-colors disabled:opacity-50"
                >
                  <Download className="h-4 w-4" />
                  Export CSV
                </button>
                <button
                  onClick={handleReset}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-medium transition-all duration-150 shadow-sm hover:shadow"
                >
                  <RefreshCw className="h-4 w-4" />
                  New File
                </button>
              </div>
            </div>

            {/* Filters */}
            <Card>
              <CardContent className="pt-6">
                <div className="flex gap-4 flex-wrap">
                  <div className="flex flex-col gap-1.5">
                    <label className="text-sm font-medium text-foreground">Payer</label>
                    <select
                      value={selectedPayer}
                      onChange={(e) => {
                        const newPayer = e.target.value
                        setSelectedPayer(newPayer)
                        handleFilterChange(newPayer, selectedServiceType)
                      }}
                      className="px-3 py-2 rounded-md border border-border bg-background text-foreground text-sm min-w-[200px]"
                    >
                      <option value="">All Payers</option>
                      {filters.payers.map(payer => (
                        <option key={payer} value={payer}>{payer}</option>
                      ))}
                    </select>
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-sm font-medium text-foreground">Service Type</label>
                    <select
                      value={selectedServiceType}
                      onChange={(e) => {
                        const newServiceType = e.target.value
                        setSelectedServiceType(newServiceType)
                        handleFilterChange(selectedPayer, newServiceType)
                      }}
                      className="px-3 py-2 rounded-md border border-border bg-background text-foreground text-sm min-w-[200px]"
                    >
                      <option value="">All Service Types</option>
                      {filters.service_types.map(type => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Matrix Table */}
            <Card>
              <CardHeader>
                <CardTitle>Aggregate Waterfall</CardTitle>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                  </div>
                ) : matrixData && matrixData.matrix.length > 0 ? (
                  <PayerMatrix data={matrixData} />
                ) : (
                  <div className="text-center py-12 text-muted-foreground">
                    No data available for the selected filters.
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Footer */}
            <div className="border-t border-border pt-8 mt-8">
              <p className="text-sm text-muted-foreground text-center">
                Your data is processed locally and is not stored on our servers.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App

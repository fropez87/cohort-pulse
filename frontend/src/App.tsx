import { useState } from 'react'
import { Header } from './components/Header'
import { FileUpload } from './components/FileUpload'
import { MetricCard } from './components/MetricCard'
import { InsightCard } from './components/InsightCard'
import { RetentionCurve, CohortSizeChart } from './components/Charts'
import { CohortHeatmap } from './components/CohortHeatmap'
import { DashboardSkeleton } from './components/LoadingState'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card'
import type { AnalysisData } from './types'
import {
  ShoppingCart,
  Users,
  DollarSign,
  TrendingUp,
  Repeat,
  Calendar,
  Download,
} from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [data, setData] = useState<AnalysisData | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileSelect = async (file: File) => {
    setIsLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        body: formData,
      })

      const result: AnalysisData = await response.json()

      if (!result.success) {
        throw new Error(result.error || 'Analysis failed')
      }

      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
      setData(null)
    } finally {
      setIsLoading(false)
    }
  }

  const handleExport = async () => {
    // Would need to re-upload file for export - simplified for demo
    alert('Export functionality - would download Excel file')
  }

  return (
    <div className="min-h-screen bg-gradient-subtle">
      <Header />

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Hero Section */}
        {!data && !isLoading && (
          <div className="max-w-2xl mx-auto text-center mb-12 animate-fade-in">
            <h2 className="text-3xl font-bold text-foreground mb-4">
              Understand your customer retention
            </h2>
            <p className="text-lg text-muted-foreground mb-2">
              Upload your order data to get instant cohort analysis and actionable insights.
            </p>
            <p className="text-sm text-muted-foreground/70">
              Your data is processed locally and is not stored on our servers.
            </p>
          </div>
        )}

        {/* File Upload */}
        {!data && !isLoading && (
          <div className="max-w-xl mx-auto mb-12">
            <FileUpload onFileSelect={handleFileSelect} isLoading={isLoading} />
            {error && (
              <div className="mt-4 p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
                {error}
              </div>
            )}
          </div>
        )}

        {/* Loading State */}
        {isLoading && <DashboardSkeleton />}

        {/* Dashboard */}
        {data && data.success && (
          <div className="space-y-8">
            {/* Upload new file button */}
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-foreground">Dashboard</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  {data.summary?.date_range}
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleExport}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 text-foreground text-sm font-medium transition-colors"
                >
                  <Download className="h-4 w-4" />
                  Export
                </button>
                <button
                  onClick={() => setData(null)}
                  className="px-4 py-2 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-medium transition-colors shadow-lg shadow-primary/25"
                >
                  New Analysis
                </button>
              </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <MetricCard
                title="Total Orders"
                value={data.summary?.total_orders || 0}
                icon={ShoppingCart}
                format="number"
                delay={0}
              />
              <MetricCard
                title="Unique Customers"
                value={data.summary?.unique_customers || 0}
                icon={Users}
                format="number"
                delay={100}
              />
              <MetricCard
                title="Total Revenue"
                value={data.summary?.total_revenue || 0}
                icon={DollarSign}
                format="currency"
                delay={200}
              />
              <MetricCard
                title="Avg Order Value"
                value={data.metrics?.aov || 0}
                icon={TrendingUp}
                format="currency"
                delay={300}
              />
              <MetricCard
                title="Customer LTV"
                value={data.metrics?.ltv || 0}
                icon={Calendar}
                format="currency"
                delay={400}
              />
              <MetricCard
                title="Repeat Rate"
                value={data.metrics?.repeat_rate || 0}
                icon={Repeat}
                format="percent"
                delay={500}
              />
            </div>

            {/* Insights */}
            {data.insights && data.insights.length > 0 && (
              <Card className="opacity-0 animate-fade-in animate-delay-100">
                <CardHeader>
                  <CardTitle>Key Insights</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {data.insights.map((insight, index) => (
                      <InsightCard
                        key={index}
                        type={insight.type}
                        title={insight.title}
                        text={insight.text}
                        delay={index * 100}
                      />
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {data.retention_curve && <RetentionCurve data={data.retention_curve} />}
              {data.cohort_sizes && <CohortSizeChart data={data.cohort_sizes} />}
            </div>

            {/* Cohort Tables */}
            <Card className="opacity-0 animate-fade-in animate-delay-400">
              <CardHeader>
                <CardTitle>Cohort Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="retention" className="w-full">
                  <TabsList className="mb-4">
                    <TabsTrigger value="retention">Customer Retention %</TabsTrigger>
                    <TabsTrigger value="customers">Customer Count</TabsTrigger>
                    <TabsTrigger value="revenue_retention">Revenue Retention %</TabsTrigger>
                    <TabsTrigger value="revenue">Revenue $</TabsTrigger>
                  </TabsList>

                  <TabsContent value="retention">
                    {data.retention_table && (
                      <CohortHeatmap data={data.retention_table} type="retention" />
                    )}
                  </TabsContent>

                  <TabsContent value="customers">
                    {data.customer_table && (
                      <CohortHeatmap data={data.customer_table} type="customers" />
                    )}
                  </TabsContent>

                  <TabsContent value="revenue_retention">
                    {data.revenue_retention_table && (
                      <CohortHeatmap data={data.revenue_retention_table} type="revenue_retention" />
                    )}
                  </TabsContent>

                  <TabsContent value="revenue">
                    {data.revenue_table && (
                      <CohortHeatmap data={data.revenue_table} type="revenue" />
                    )}
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>

            {/* Footer */}
            <div className="text-center py-8 text-sm text-muted-foreground">
              <p>Your data is processed locally and is not stored on our servers.</p>
              <p className="mt-2 font-medium">Cohort Pulse</p>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App

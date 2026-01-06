// Common types
export type AnalysisType = 'retention' | 'waterfall'

// Waterfall (Healthcare) types
export interface WaterfallUploadResponse {
  message: string
  rows: number
  filters: {
    payers: string[]
    service_types: string[]
  }
  // Include matrix data in upload response for serverless compatibility
  data?: Array<Record<string, unknown>>
  matrix?: MatrixRow[]
  payment_months?: string[]
  totals?: {
    gross_charge: number
    payments: Record<string, number>
  }
}

export interface MatrixRow {
  dos_month: string
  gross_charge: number
  payments: Record<string, number>
}

export interface CohortMatrixData {
  matrix: MatrixRow[]
  payment_months: string[]
  totals: {
    gross_charge: number
    payments: Record<string, number>
  }
}

export interface WaterfallFiltersData {
  payers: string[]
  service_types: string[]
}

// Retention (Subscription) types
export interface RetentionAnalysisResponse {
  success: boolean
  error?: string
  summary?: {
    total_orders: number
    unique_customers: number
    total_revenue: number
    date_range: string
  }
  metrics?: {
    aov: number
    ltv: number
    repeat_rate: number
  }
  insights?: Array<{
    type: string
    title: string
    text: string
  }>
  retention_table?: Record<string, Record<string, number>>
  revenue_table?: Record<string, Record<string, number>>
  customer_table?: Record<string, Record<string, number>>
  revenue_retention_table?: Record<string, Record<string, number>>
  cohort_sizes?: Array<{
    cohort_month: string
    new_customers: number
  }>
  retention_curve?: Array<{
    month: number
    retention: number
  }>
}

// Legacy aliases for backwards compatibility
export type UploadResponse = WaterfallUploadResponse
export type FiltersData = WaterfallFiltersData

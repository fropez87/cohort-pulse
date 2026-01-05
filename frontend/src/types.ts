export interface AnalysisData {
  success: boolean
  error?: string
  summary?: {
    total_orders: number
    unique_customers: number
    total_revenue: number
    date_range: string
    num_cohorts: number
  }
  metrics?: {
    ltv: number
    aov: number
    repeat_rate: number
    avg_orders_per_customer: number
    repeat_customers: number
    one_time_customers: number
  }
  insights?: Array<{
    type: 'positive' | 'warning' | 'info'
    title: string
    text: string
  }>
  retention_table?: Record<string, Record<string, number | null>>
  revenue_table?: Record<string, Record<string, number | null>>
  customer_table?: Record<string, Record<string, number | null>>
  revenue_retention_table?: Record<string, Record<string, number | null>>
  cohort_sizes?: Array<{ cohort_month: string; new_customers: number }>
  retention_curve?: Array<{ month: number; retention: number }>
}

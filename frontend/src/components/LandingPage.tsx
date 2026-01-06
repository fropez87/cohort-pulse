import { FileUpload } from './FileUpload'
import { Card, CardContent } from './ui/card'
import {
  Upload,
  BarChart3,
  Download,
  Shield,
  Zap,
  LineChart,
  Table2,
  Lightbulb,
  FileSpreadsheet,
  CheckCircle2,
  ArrowRight,
} from 'lucide-react'

interface LandingPageProps {
  onFileSelect: (file: File) => void
  isLoading: boolean
  error: string | null
}

// Sample data for preview
const sampleMetrics = [
  { label: 'Total Orders', value: '12,847' },
  { label: 'Unique Customers', value: '4,231' },
  { label: 'Total Revenue', value: '$847,392' },
  { label: 'Repeat Rate', value: '34.2%' },
]

const sampleHeatmapData = [
  { cohort: 'Jan 2024', m0: '100%', m1: '42%', m2: '28%', m3: '21%' },
  { cohort: 'Feb 2024', m0: '100%', m1: '38%', m2: '25%', m3: '19%' },
  { cohort: 'Mar 2024', m0: '100%', m1: '45%', m2: '31%', m3: '-' },
  { cohort: 'Apr 2024', m0: '100%', m1: '41%', m2: '-', m3: '-' },
]

export function LandingPage({ onFileSelect, isLoading, error }: LandingPageProps) {
  return (
    <div className="space-y-16 pb-16">
      {/* Hero Section */}
      <section className="max-w-4xl mx-auto text-center pt-8 animate-fade-in">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
          <Zap className="h-4 w-4" />
          Free cohort analysis in seconds
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-6 leading-tight">
          Turn your order data into
          <span className="text-primary"> retention insights</span>
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          Upload a CSV or Excel file with your orders and instantly get cohort analysis,
          retention curves, and actionable insights to grow your business.
        </p>

        {/* Upload Section */}
        <div className="max-w-xl mx-auto mb-6">
          <FileUpload onFileSelect={onFileSelect} isLoading={isLoading} />
          {error && (
            <div className="mt-4 p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
              {error}
            </div>
          )}
        </div>

        <p className="text-sm text-muted-foreground/70 flex items-center justify-center gap-2">
          <Shield className="h-4 w-4" />
          Your data is processed securely and never stored on our servers
        </p>
      </section>

      {/* Features */}
      <section className="max-w-5xl mx-auto">
        <h2 className="text-2xl font-bold text-foreground text-center mb-8">
          What you'll get
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            icon={BarChart3}
            title="Key Metrics"
            description="Total revenue, customer count, AOV, lifetime value, and repeat purchase rate at a glance."
          />
          <FeatureCard
            icon={Table2}
            title="Cohort Tables"
            description="Month-over-month retention and revenue tables showing how each cohort performs over time."
          />
          <FeatureCard
            icon={LineChart}
            title="Retention Curves"
            description="Visual charts showing customer retention patterns and cohort size trends."
          />
          <FeatureCard
            icon={Lightbulb}
            title="AI Insights"
            description="Automatically generated insights highlighting your best cohorts and growth opportunities."
          />
          <FeatureCard
            icon={Download}
            title="Excel Export"
            description="Download your complete analysis as a formatted Excel file to share with your team."
          />
          <FeatureCard
            icon={Zap}
            title="Instant Results"
            description="No signup required. Upload your file and get results in seconds, completely free."
          />
        </div>
      </section>

      {/* File Format Section */}
      <section className="max-w-4xl mx-auto">
        <Card className="border-2 border-dashed">
          <CardContent className="p-8">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3 rounded-xl bg-primary/10">
                <FileSpreadsheet className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-foreground mb-2">
                  File Format Requirements
                </h3>
                <p className="text-muted-foreground">
                  Your CSV or Excel file should contain order-level data with these columns:
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <h4 className="font-medium text-foreground mb-3">Required Columns</h4>
                <ul className="space-y-2">
                  <RequirementItem text="Customer ID or Email" required />
                  <RequirementItem text="Order Date" required />
                  <RequirementItem text="Order Total / Revenue" required />
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-foreground mb-3">Optional Columns</h4>
                <ul className="space-y-2">
                  <RequirementItem text="Order ID" />
                  <RequirementItem text="Product Name" />
                  <RequirementItem text="Any other columns (will be ignored)" />
                </ul>
              </div>
            </div>

            <div className="bg-muted/50 rounded-lg p-4">
              <h4 className="font-medium text-foreground mb-3">Example Data</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-2 px-3 font-medium text-muted-foreground">customer_email</th>
                      <th className="text-left py-2 px-3 font-medium text-muted-foreground">order_date</th>
                      <th className="text-left py-2 px-3 font-medium text-muted-foreground">total</th>
                    </tr>
                  </thead>
                  <tbody className="font-mono text-xs">
                    <tr className="border-b border-border/50">
                      <td className="py-2 px-3">john@example.com</td>
                      <td className="py-2 px-3">2024-01-15</td>
                      <td className="py-2 px-3">89.99</td>
                    </tr>
                    <tr className="border-b border-border/50">
                      <td className="py-2 px-3">jane@example.com</td>
                      <td className="py-2 px-3">2024-01-18</td>
                      <td className="py-2 px-3">149.00</td>
                    </tr>
                    <tr>
                      <td className="py-2 px-3">john@example.com</td>
                      <td className="py-2 px-3">2024-02-22</td>
                      <td className="py-2 px-3">65.50</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <p className="text-sm text-muted-foreground mt-4">
              <strong>Tip:</strong> Export your orders from Shopify, WooCommerce, Stripe, or any e-commerce platform.
              We'll automatically detect the column names.
            </p>
          </CardContent>
        </Card>
      </section>

      {/* Sample Output Preview */}
      <section className="max-w-5xl mx-auto">
        <h2 className="text-2xl font-bold text-foreground text-center mb-2">
          Sample Output Preview
        </h2>
        <p className="text-muted-foreground text-center mb-8">
          Here's what your analysis will look like
        </p>

        <div className="space-y-6">
          {/* Metrics Preview */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {sampleMetrics.map((metric, index) => (
              <Card key={index} className="bg-white/50">
                <CardContent className="p-4">
                  <p className="text-sm text-muted-foreground mb-1">{metric.label}</p>
                  <p className="text-2xl font-bold text-foreground">{metric.value}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Heatmap Preview */}
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold text-foreground mb-4">Customer Retention by Cohort</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-2 px-3 font-medium text-muted-foreground">Cohort</th>
                      <th className="text-center py-2 px-3 font-medium text-muted-foreground">Month 0</th>
                      <th className="text-center py-2 px-3 font-medium text-muted-foreground">Month 1</th>
                      <th className="text-center py-2 px-3 font-medium text-muted-foreground">Month 2</th>
                      <th className="text-center py-2 px-3 font-medium text-muted-foreground">Month 3</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sampleHeatmapData.map((row, index) => (
                      <tr key={index} className="border-b border-border/50">
                        <td className="py-2 px-3 font-medium">{row.cohort}</td>
                        <td className="py-2 px-3 text-center">
                          <span className="inline-block px-3 py-1 rounded bg-primary/60 text-white text-xs font-medium">
                            {row.m0}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-center">
                          <span className="inline-block px-3 py-1 rounded bg-primary/40 text-white text-xs font-medium">
                            {row.m1}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-center">
                          {row.m2 !== '-' ? (
                            <span className="inline-block px-3 py-1 rounded bg-primary/30 text-foreground text-xs font-medium">
                              {row.m2}
                            </span>
                          ) : (
                            <span className="text-muted-foreground">-</span>
                          )}
                        </td>
                        <td className="py-2 px-3 text-center">
                          {row.m3 !== '-' ? (
                            <span className="inline-block px-3 py-1 rounded bg-primary/25 text-foreground text-xs font-medium">
                              {row.m3}
                            </span>
                          ) : (
                            <span className="text-muted-foreground">-</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Insight Preview */}
          <Card className="bg-amber-50/50 border-amber-200/50">
            <CardContent className="p-4 flex items-start gap-3">
              <Lightbulb className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-medium text-foreground">Best Performing Cohort</p>
                <p className="text-sm text-muted-foreground">
                  March 2024 cohort shows 45% Month 1 retention, 7% higher than average.
                  Consider analyzing what marketing campaigns or product changes drove this improvement.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-2xl mx-auto text-center">
        <Card className="bg-primary/5 border-primary/20">
          <CardContent className="p-8">
            <h2 className="text-2xl font-bold text-foreground mb-4">
              Ready to analyze your data?
            </h2>
            <p className="text-muted-foreground mb-6">
              Upload your order export and get insights in seconds. No signup, no credit card, completely free.
            </p>
            <button
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground font-medium transition-colors"
            >
              <Upload className="h-5 w-5" />
              Upload Your Data
              <ArrowRight className="h-4 w-4" />
            </button>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t border-border pt-8">
        <div className="max-w-3xl mx-auto text-center space-y-4">
          <div className="text-xs text-muted-foreground/70 space-y-2">
            <p>
              <strong>Disclaimer:</strong> This tool is provided for informational and educational purposes only.
              The analysis, metrics, and insights generated are based solely on the data you provide and may contain
              errors, inaccuracies, or omissions. We make no representations or warranties regarding the accuracy,
              completeness, or reliability of any results.
            </p>
            <p>
              Cohort Pulse does not verify the authenticity or validity of uploaded data. Any business decisions
              made based on this analysis are at your own risk. This tool should not be used as the sole basis
              for financial, strategic, or operational decisions. Always consult with qualified professionals
              and verify results independently before taking action.
            </p>
          </div>
          <p className="text-sm font-medium text-muted-foreground pt-2">Cohort Pulse</p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon: Icon, title, description }: { icon: React.ElementType; title: string; description: string }) {
  return (
    <Card className="bg-white/50 hover:bg-white/80 transition-colors">
      <CardContent className="p-6">
        <div className="p-2 rounded-lg bg-primary/10 w-fit mb-4">
          <Icon className="h-5 w-5 text-primary" />
        </div>
        <h3 className="font-semibold text-foreground mb-2">{title}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  )
}

function RequirementItem({ text, required }: { text: string; required?: boolean }) {
  return (
    <li className="flex items-center gap-2 text-sm">
      <CheckCircle2 className={`h-4 w-4 flex-shrink-0 ${required ? 'text-primary' : 'text-muted-foreground/50'}`} />
      <span className={required ? 'text-foreground' : 'text-muted-foreground'}>{text}</span>
      {required && <span className="text-xs text-primary font-medium">Required</span>}
    </li>
  )
}

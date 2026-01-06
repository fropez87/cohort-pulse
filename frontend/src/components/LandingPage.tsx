import { useState } from 'react'
import { FileUpload } from './FileUpload'
import { Card, CardContent } from './ui/card'
import {
  Upload,
  Download,
  Shield,
  Zap,
  Table2,
  FileSpreadsheet,
  CheckCircle2,
  ArrowRight,
  Filter,
  TrendingUp,
  Building2,
  Stethoscope,
} from 'lucide-react'
import { cn } from '../lib/utils'

export type AnalysisType = 'retention' | 'waterfall'

interface LandingPageProps {
  onFileSelect: (file: File, analysisType: AnalysisType) => void
  isLoading: boolean
  error: string | null
}

// Content configuration for each analysis type
const analysisConfig = {
  retention: {
    badge: 'Customer retention analysis in seconds',
    title: 'Turn your order data into',
    titleHighlight: ' retention insights',
    description: 'Upload a CSV with your customer orders to instantly see how retention and revenue flow over time by acquisition cohort.',
    features: [
      {
        icon: Table2,
        title: 'Retention Matrix',
        description: 'Cohort months as rows, periods as columns showing customer retention percentages over time.',
      },
      {
        icon: TrendingUp,
        title: 'Revenue & LTV',
        description: 'Track revenue retention, calculate customer lifetime value, and identify your best cohorts.',
      },
      {
        icon: Download,
        title: 'Excel Export',
        description: 'Download all cohort tables as a formatted Excel file to share with your team.',
      },
    ],
    requiredColumns: [
      { name: 'order_date', description: 'Date of the order/transaction' },
      { name: 'customer_id', description: 'Unique identifier for each customer' },
      { name: 'order_amount', description: 'Revenue amount for the order' },
    ],
    sampleData: [
      { order_date: '2024-01-15', customer_id: 'C001', order_amount: '99.99' },
      { order_date: '2024-01-20', customer_id: 'C002', order_amount: '149.50' },
      { order_date: '2024-02-10', customer_id: 'C001', order_amount: '79.99' },
      { order_date: '2024-02-15', customer_id: 'C003', order_amount: '199.00' },
    ],
    sampleOutput: {
      title: 'Customer Retention %',
      headers: ['Cohort', 'Size', 'Month 0', 'Month 1', 'Month 2', 'Month 3'],
      rows: [
        { cohort: '2024-01', size: '1,250', m0: '100%', m1: '42%', m2: '28%', m3: '21%' },
        { cohort: '2024-02', size: '1,480', m0: '100%', m1: '45%', m2: '31%', m3: '' },
        { cohort: '2024-03', size: '1,320', m0: '100%', m1: '39%', m2: '', m3: '' },
      ],
    },
    ctaTitle: 'Ready to analyze your customers?',
    ctaDescription: 'Upload your order data and see your retention metrics instantly. No signup required.',
    note: 'Customers are grouped by their first order month. Subsequent orders track retention.',
    columnChips: ['order_date', 'customer_id', 'order_amount'],
  },
  waterfall: {
    badge: 'Payment cohort analysis in seconds',
    title: 'Turn your payment data into',
    titleHighlight: ' collection insights',
    description: 'Upload a CSV with your claims and payments to instantly see how collections flow over time by date of service cohort.',
    features: [
      {
        icon: Table2,
        title: 'Cohort Matrix',
        description: 'DOS months as rows, payment months as columns showing exactly when cash hits for each service cohort.',
      },
      {
        icon: Filter,
        title: 'Payer & Service Filters',
        description: 'Filter by payer and service type to drill down into specific collection patterns.',
      },
      {
        icon: Download,
        title: 'CSV Export',
        description: 'Download the filtered matrix as a CSV to use in Excel or share with your team.',
      },
    ],
    requiredColumns: [
      { name: 'claim_id', description: 'Unique identifier per claim' },
      { name: 'service_date', description: 'Date of service (DOS)' },
      { name: 'date_paid', description: 'Date payment was received' },
      { name: 'billed_amount', description: 'Gross charge amount' },
      { name: 'amount_paid', description: 'Payment amount (can be negative)' },
      { name: 'payer', description: 'Insurance/payer name' },
      { name: 'service_type', description: 'Type of service' },
    ],
    sampleData: [
      { claim_id: 'CLM001', service_date: '2024-01-15', date_paid: '2024-02-10', billed_amount: '500.00', amount_paid: '425.00', payer: 'Blue Cross', service_type: 'Office Visit' },
      { claim_id: 'CLM001', service_date: '2024-01-15', date_paid: '2024-03-05', billed_amount: '500.00', amount_paid: '50.00', payer: 'Blue Cross', service_type: 'Office Visit' },
      { claim_id: 'CLM002', service_date: '2024-02-20', date_paid: '2024-03-15', billed_amount: '1200.00', amount_paid: '960.00', payer: 'Aetna', service_type: 'Lab Work' },
    ],
    sampleOutput: {
      title: 'Aggregate Waterfall',
      headers: ['DOS Month', 'Gross Charge', '2024-01', '2024-02', '2024-03'],
      rows: [
        { dos: '2024-01', gross: '125,000', m1: '45,000', m2: '32,000', m3: '18,000' },
        { dos: '2024-02', gross: '142,000', m1: '', m2: '52,000', m3: '38,000' },
        { dos: '2024-03', gross: '138,000', m1: '', m2: '', m3: '61,000' },
      ],
      totals: { label: 'Grand Totals', gross: '405,000', m1: '45,000', m2: '84,000', m3: '117,000' },
    },
    ctaTitle: 'Ready to analyze your payments?',
    ctaDescription: 'Upload your payment data and see your collection waterfall instantly. No signup required.',
    note: 'Multiple payments per claim are supported - the same claim_id can appear multiple times with different payment dates. Gross charge is deduplicated by claim_id.',
    columnChips: ['claim_id', 'service_date', 'date_paid', 'amount_paid', 'payer'],
  },
}

export function LandingPage({ onFileSelect, isLoading, error }: LandingPageProps) {
  const [analysisType, setAnalysisType] = useState<AnalysisType>('retention')
  const config = analysisConfig[analysisType]

  const handleFileSelect = (file: File) => {
    onFileSelect(file, analysisType)
  }

  return (
    <div className="space-y-16 pb-16">
      {/* Hero Section */}
      <section className="max-w-4xl mx-auto text-center pt-8 animate-fade-in">
        {/* Analysis Type Toggle */}
        <div className="flex justify-center mb-10">
          <div className="inline-flex flex-col sm:flex-row gap-3">
            <button
              onClick={() => setAnalysisType('retention')}
              className={cn(
                "flex items-center gap-3 px-6 py-4 rounded-xl text-base font-semibold transition-all duration-200 border-2",
                analysisType === 'retention'
                  ? "bg-primary text-primary-foreground border-primary shadow-lg shadow-primary/25 scale-[1.02]"
                  : "bg-white text-muted-foreground border-border hover:border-primary/50 hover:text-foreground hover:shadow-md"
              )}
            >
              <Building2 className={cn("h-5 w-5", analysisType === 'retention' ? "text-primary-foreground" : "text-primary")} />
              <div className="text-left">
                <div>Subscription Business</div>
                <div className={cn("text-xs font-normal", analysisType === 'retention' ? "text-primary-foreground/80" : "text-muted-foreground")}>
                  Retention Analytics
                </div>
              </div>
            </button>
            <button
              onClick={() => setAnalysisType('waterfall')}
              className={cn(
                "flex items-center gap-3 px-6 py-4 rounded-xl text-base font-semibold transition-all duration-200 border-2",
                analysisType === 'waterfall'
                  ? "bg-primary text-primary-foreground border-primary shadow-lg shadow-primary/25 scale-[1.02]"
                  : "bg-white text-muted-foreground border-border hover:border-primary/50 hover:text-foreground hover:shadow-md"
              )}
            >
              <Stethoscope className={cn("h-5 w-5", analysisType === 'waterfall' ? "text-primary-foreground" : "text-primary")} />
              <div className="text-left">
                <div>Healthcare Business</div>
                <div className={cn("text-xs font-normal", analysisType === 'waterfall' ? "text-primary-foreground/80" : "text-muted-foreground")}>
                  Payer Waterfall
                </div>
              </div>
            </button>
          </div>
        </div>

        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
          <Zap className="h-4 w-4" />
          {config.badge}
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-6 leading-tight">
          {config.title}
          <span className="text-primary">{config.titleHighlight}</span>
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          {config.description}
        </p>

        {/* Upload Section */}
        <div className="max-w-xl mx-auto mb-6">
          <FileUpload
            onFileSelect={handleFileSelect}
            isLoading={isLoading}
            columnChips={config.columnChips}
          />
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
          {config.features.map((feature, index) => (
            <FeatureCard
              key={index}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
            />
          ))}
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
                  Your CSV file should contain {analysisType === 'retention' ? 'order-level' : 'payment-level'} data with these columns:
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <h4 className="font-medium text-foreground mb-3">Required Columns</h4>
                <ul className="space-y-2">
                  {config.requiredColumns.map((col) => (
                    <RequirementItem key={col.name} text={col.name} required />
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-foreground mb-3">Column Descriptions</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  {config.requiredColumns.map((col) => (
                    <li key={col.name}><strong>{col.name}</strong> - {col.description}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="bg-muted/50 rounded-lg p-4">
              <h4 className="font-medium text-foreground mb-3">Example Data</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      {config.requiredColumns.map((col) => (
                        <th key={col.name} className="text-left py-2 px-2 font-medium text-muted-foreground">
                          {col.name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="font-mono text-xs">
                    {config.sampleData.map((row, index) => (
                      <tr key={index} className={index < config.sampleData.length - 1 ? 'border-b border-border/50' : ''}>
                        {config.requiredColumns.map((col) => (
                          <td key={col.name} className="py-2 px-2">
                            {(row as Record<string, string>)[col.name]}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <p className="text-sm text-muted-foreground mt-4">
              <strong>Note:</strong> {config.note}
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
          Here's what your {analysisType === 'retention' ? 'retention matrix' : 'waterfall matrix'} will look like
        </p>

        <Card>
          <CardContent className="p-6">
            <h3 className="font-semibold text-foreground mb-4">{config.sampleOutput.title}</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm font-mono">
                <thead>
                  <tr className="border-b border-border bg-muted">
                    {config.sampleOutput.headers.map((header, index) => (
                      <th
                        key={index}
                        className={cn(
                          "py-2 px-3 font-semibold text-foreground",
                          index === 0 ? "text-left" : "text-right",
                          analysisType === 'waterfall' && index === 1 && "bg-blue-50"
                        )}
                      >
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {analysisType === 'retention' ? (
                    config.sampleOutput.rows.map((row: any, index: number) => (
                      <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'}>
                        <td className="py-2 px-3 font-medium">{row.cohort}</td>
                        <td className="py-2 px-3 text-right">{row.size}</td>
                        <td className="py-2 px-3 text-right">{row.m0}</td>
                        <td className="py-2 px-3 text-right">{row.m1}</td>
                        <td className="py-2 px-3 text-right">{row.m2}</td>
                        <td className="py-2 px-3 text-right">{row.m3}</td>
                      </tr>
                    ))
                  ) : (
                    <>
                      {config.sampleOutput.rows.map((row: any, index: number) => (
                        <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'}>
                          <td className="py-2 px-3 font-medium">{row.dos}</td>
                          <td className="py-2 px-3 text-right bg-blue-50/50 font-semibold">{row.gross}</td>
                          <td className="py-2 px-3 text-right">{row.m1}</td>
                          <td className="py-2 px-3 text-right">{row.m2}</td>
                          <td className="py-2 px-3 text-right">{row.m3}</td>
                        </tr>
                      ))}
                      {(config.sampleOutput as any).totals && (
                        <tr className="bg-muted font-bold border-t-2">
                          <td className="py-2 px-3">{(config.sampleOutput as any).totals.label}</td>
                          <td className="py-2 px-3 text-right bg-blue-100">{(config.sampleOutput as any).totals.gross}</td>
                          <td className="py-2 px-3 text-right">{(config.sampleOutput as any).totals.m1}</td>
                          <td className="py-2 px-3 text-right">{(config.sampleOutput as any).totals.m2}</td>
                          <td className="py-2 px-3 text-right">{(config.sampleOutput as any).totals.m3}</td>
                        </tr>
                      )}
                    </>
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* CTA Section */}
      <section className="max-w-2xl mx-auto text-center">
        <Card className="bg-primary/5 border-primary/20">
          <CardContent className="p-8">
            <h2 className="text-2xl font-bold text-foreground mb-4">
              {config.ctaTitle}
            </h2>
            <p className="text-muted-foreground mb-6">
              {config.ctaDescription}
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
          <div className="text-xs text-muted-foreground/70 space-y-3">
            <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-800">
              <p className="font-semibold mb-1">Important Privacy & Compliance Notice</p>
              <p>
                Do NOT upload files containing Personally Identifiable Information (PII), Protected Health Information (PHI),
                or any sensitive data. This tool is NOT HIPAA compliant. For healthcare analytics, ensure all data is
                fully de-identified before uploading. By using this tool, you confirm that your data contains no PII or PHI.
              </p>
            </div>
            <p>
              <strong>Disclaimer:</strong> This tool is provided for informational and educational purposes only.
              The analysis generated is based solely on the data you provide and may contain
              errors or omissions. We make no representations regarding the accuracy or reliability of any results.
            </p>
          </div>
          <div className="pt-4 border-t border-border">
            <p className="text-sm font-medium text-muted-foreground">Cohort Pulse</p>
            <p className="text-xs text-muted-foreground/60 mt-1">
              &copy; {new Date().getFullYear()} Cohort Pulse. All rights reserved.
            </p>
          </div>
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
    </li>
  )
}

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
} from 'lucide-react'

interface LandingPageProps {
  onFileSelect: (file: File) => void
  isLoading: boolean
  error: string | null
}

// Sample waterfall data for preview
const sampleWaterfallData = [
  { dos: '2024-01', gross: '125,000', jan: '45,000', feb: '32,000', mar: '18,000' },
  { dos: '2024-02', gross: '142,000', jan: '', feb: '52,000', mar: '38,000' },
  { dos: '2024-03', gross: '138,000', jan: '', feb: '', mar: '61,000' },
]

export function LandingPage({ onFileSelect, isLoading, error }: LandingPageProps) {
  return (
    <div className="space-y-16 pb-16">
      {/* Hero Section */}
      <section className="max-w-4xl mx-auto text-center pt-8 animate-fade-in">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
          <Zap className="h-4 w-4" />
          Payment cohort analysis in seconds
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-6 leading-tight">
          Turn your payment data into
          <span className="text-primary"> collection insights</span>
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          Upload a CSV with your claims and payments to instantly see how collections
          flow over time by date of service cohort.
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
            icon={Table2}
            title="Cohort Matrix"
            description="DOS months as rows, payment months as columns showing exactly when cash hits for each service cohort."
          />
          <FeatureCard
            icon={Filter}
            title="Payer & Service Filters"
            description="Filter by payer and service type to drill down into specific collection patterns."
          />
          <FeatureCard
            icon={Download}
            title="CSV Export"
            description="Download the filtered matrix as a CSV to use in Excel or share with your team."
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
                  Your CSV file should contain payment-level data with these columns:
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <h4 className="font-medium text-foreground mb-3">Required Columns</h4>
                <ul className="space-y-2">
                  <RequirementItem text="claim_id" required />
                  <RequirementItem text="service_date" required />
                  <RequirementItem text="date_paid" required />
                  <RequirementItem text="billed_amount" required />
                  <RequirementItem text="amount_paid" required />
                  <RequirementItem text="payer" required />
                  <RequirementItem text="service_type" required />
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-foreground mb-3">Column Descriptions</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li><strong>claim_id</strong> - Unique identifier per claim</li>
                  <li><strong>service_date</strong> - Date of service (DOS)</li>
                  <li><strong>date_paid</strong> - Date payment was received</li>
                  <li><strong>billed_amount</strong> - Gross charge amount</li>
                  <li><strong>amount_paid</strong> - Payment amount (can be negative)</li>
                  <li><strong>payer</strong> - Insurance/payer name</li>
                  <li><strong>service_type</strong> - Type of service</li>
                </ul>
              </div>
            </div>

            <div className="bg-muted/50 rounded-lg p-4">
              <h4 className="font-medium text-foreground mb-3">Example Data</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-2 px-2 font-medium text-muted-foreground">claim_id</th>
                      <th className="text-left py-2 px-2 font-medium text-muted-foreground">service_date</th>
                      <th className="text-left py-2 px-2 font-medium text-muted-foreground">date_paid</th>
                      <th className="text-left py-2 px-2 font-medium text-muted-foreground">billed_amount</th>
                      <th className="text-left py-2 px-2 font-medium text-muted-foreground">amount_paid</th>
                      <th className="text-left py-2 px-2 font-medium text-muted-foreground">payer</th>
                      <th className="text-left py-2 px-2 font-medium text-muted-foreground">service_type</th>
                    </tr>
                  </thead>
                  <tbody className="font-mono text-xs">
                    <tr className="border-b border-border/50">
                      <td className="py-2 px-2">CLM001</td>
                      <td className="py-2 px-2">2024-01-15</td>
                      <td className="py-2 px-2">2024-02-10</td>
                      <td className="py-2 px-2">500.00</td>
                      <td className="py-2 px-2">425.00</td>
                      <td className="py-2 px-2">Blue Cross</td>
                      <td className="py-2 px-2">Office Visit</td>
                    </tr>
                    <tr className="border-b border-border/50">
                      <td className="py-2 px-2">CLM001</td>
                      <td className="py-2 px-2">2024-01-15</td>
                      <td className="py-2 px-2">2024-03-05</td>
                      <td className="py-2 px-2">500.00</td>
                      <td className="py-2 px-2">50.00</td>
                      <td className="py-2 px-2">Blue Cross</td>
                      <td className="py-2 px-2">Office Visit</td>
                    </tr>
                    <tr>
                      <td className="py-2 px-2">CLM002</td>
                      <td className="py-2 px-2">2024-02-20</td>
                      <td className="py-2 px-2">2024-03-15</td>
                      <td className="py-2 px-2">1200.00</td>
                      <td className="py-2 px-2">960.00</td>
                      <td className="py-2 px-2">Aetna</td>
                      <td className="py-2 px-2">Lab Work</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <p className="text-sm text-muted-foreground mt-4">
              <strong>Note:</strong> Multiple payments per claim are supported - the same claim_id can appear
              multiple times with different payment dates. Gross charge is deduplicated by claim_id.
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
          Here's what your waterfall matrix will look like
        </p>

        <Card>
          <CardContent className="p-6">
            <h3 className="font-semibold text-foreground mb-4">Aggregate Waterfall</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm font-mono">
                <thead>
                  <tr className="border-b border-border bg-muted">
                    <th className="text-left py-2 px-3 font-semibold text-foreground">DOS Month</th>
                    <th className="text-right py-2 px-3 font-semibold text-foreground bg-blue-50">Gross Charge</th>
                    <th className="text-right py-2 px-3 font-semibold text-foreground">2024-01</th>
                    <th className="text-right py-2 px-3 font-semibold text-foreground">2024-02</th>
                    <th className="text-right py-2 px-3 font-semibold text-foreground">2024-03</th>
                  </tr>
                </thead>
                <tbody>
                  {sampleWaterfallData.map((row, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'}>
                      <td className="py-2 px-3 font-medium">{row.dos}</td>
                      <td className="py-2 px-3 text-right bg-blue-50/50 font-semibold">{row.gross}</td>
                      <td className="py-2 px-3 text-right">{row.jan}</td>
                      <td className="py-2 px-3 text-right">{row.feb}</td>
                      <td className="py-2 px-3 text-right">{row.mar}</td>
                    </tr>
                  ))}
                  <tr className="bg-muted font-bold border-t-2">
                    <td className="py-2 px-3">Grand Totals</td>
                    <td className="py-2 px-3 text-right bg-blue-100">405,000</td>
                    <td className="py-2 px-3 text-right">45,000</td>
                    <td className="py-2 px-3 text-right">84,000</td>
                    <td className="py-2 px-3 text-right">117,000</td>
                  </tr>
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
              Ready to analyze your payments?
            </h2>
            <p className="text-muted-foreground mb-6">
              Upload your payment data and see your collection waterfall instantly. No signup required.
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
              The analysis generated is based solely on the data you provide and may contain
              errors or omissions. We make no representations regarding the accuracy or reliability of any results.
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
    </li>
  )
}

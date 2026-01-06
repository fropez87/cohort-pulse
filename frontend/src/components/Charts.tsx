import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'

// Teal accent color matching our design system
const ACCENT_COLOR = '#2a9d8f'

interface RetentionCurveProps {
  data: Array<{ month: number; retention: number }>
}

export function RetentionCurve({ data }: RetentionCurveProps) {
  return (
    <Card className="opacity-0 animate-fade-in animate-delay-200 border border-border shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-semibold">Retention Curve</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="month"
              tick={{ fontSize: 12, fill: '#6b7280' }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
              label={{ value: 'Month', position: 'bottom', offset: -5, fontSize: 12, fill: '#6b7280' }}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
              label={{ value: 'Retention %', angle: -90, position: 'insideLeft', fontSize: 12, fill: '#6b7280' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                fontSize: '14px',
              }}
              formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Retention']}
              labelFormatter={(label) => `Month ${label}`}
            />
            <Line
              type="monotone"
              dataKey="retention"
              stroke={ACCENT_COLOR}
              strokeWidth={2}
              dot={{ fill: ACCENT_COLOR, strokeWidth: 2, r: 3 }}
              activeDot={{ r: 5, fill: ACCENT_COLOR }}
              animationDuration={1000}
              animationEasing="ease-out"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

interface CohortSizeChartProps {
  data: Array<{ cohort_month: string; new_customers: number }>
}

export function CohortSizeChart({ data }: CohortSizeChartProps) {
  return (
    <Card className="opacity-0 animate-fade-in animate-delay-300 border border-border shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-semibold">New Customers by Cohort</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
            <XAxis
              dataKey="cohort_month"
              tick={{ fontSize: 11, fill: '#6b7280' }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis
              tick={{ fontSize: 12, fill: '#6b7280' }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                fontSize: '14px',
              }}
              formatter={(value) => [Number(value).toLocaleString(), 'New Customers']}
              labelFormatter={(label) => `Cohort: ${label}`}
            />
            <Bar
              dataKey="new_customers"
              fill={ACCENT_COLOR}
              radius={[3, 3, 0, 0]}
              animationDuration={1000}
              animationEasing="ease-out"
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

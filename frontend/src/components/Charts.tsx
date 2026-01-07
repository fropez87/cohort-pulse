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

// Emerald accent color matching our dark design system
const ACCENT_COLOR = '#10b981'
const GRID_COLOR = 'rgba(255,255,255,0.08)'
const TEXT_COLOR = '#737373'

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
            <CartesianGrid strokeDasharray="3 3" stroke={GRID_COLOR} />
            <XAxis
              dataKey="month"
              tick={{ fontSize: 12, fill: TEXT_COLOR }}
              tickLine={false}
              axisLine={{ stroke: GRID_COLOR }}
              label={{ value: 'Month', position: 'bottom', offset: -5, fontSize: 12, fill: TEXT_COLOR }}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 12, fill: TEXT_COLOR }}
              tickLine={false}
              axisLine={{ stroke: GRID_COLOR }}
              label={{ value: 'Retention %', angle: -90, position: 'insideLeft', fontSize: 12, fill: TEXT_COLOR }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1a1a1a',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '6px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
                fontSize: '14px',
                color: '#fafafa',
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
            <CartesianGrid strokeDasharray="3 3" stroke={GRID_COLOR} vertical={false} />
            <XAxis
              dataKey="cohort_month"
              tick={{ fontSize: 11, fill: TEXT_COLOR }}
              tickLine={false}
              axisLine={{ stroke: GRID_COLOR }}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis
              tick={{ fontSize: 12, fill: TEXT_COLOR }}
              tickLine={false}
              axisLine={{ stroke: GRID_COLOR }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1a1a1a',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '6px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
                fontSize: '14px',
                color: '#fafafa',
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

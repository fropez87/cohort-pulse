import { cn } from '../lib/utils'

export function LoadingSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("animate-pulse rounded-lg bg-muted", className)} />
  )
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Metrics skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="p-6 rounded-xl border bg-card">
            <div className="flex justify-between items-start">
              <div className="space-y-3 flex-1">
                <LoadingSkeleton className="h-4 w-24" />
                <LoadingSkeleton className="h-8 w-32" />
              </div>
              <LoadingSkeleton className="h-12 w-12 rounded-xl" />
            </div>
          </div>
        ))}
      </div>

      {/* Charts skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[1, 2].map((i) => (
          <div key={i} className="p-6 rounded-xl border bg-card">
            <LoadingSkeleton className="h-5 w-40 mb-4" />
            <LoadingSkeleton className="h-64 w-full" />
          </div>
        ))}
      </div>

      {/* Table skeleton */}
      <div className="p-6 rounded-xl border bg-card">
        <LoadingSkeleton className="h-5 w-48 mb-6" />
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <LoadingSkeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      </div>
    </div>
  )
}

export function Spinner() {
  return (
    <div className="flex items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>
  )
}

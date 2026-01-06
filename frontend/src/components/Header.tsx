export function Header() {
  return (
    <header className="border-b border-border bg-white sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center gap-3">
          {/* Logo - clean, no gradient */}
          <div className="w-9 h-9 rounded-lg bg-primary flex items-center justify-center">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="8" stroke="white" strokeWidth="1.5" fill="none" opacity="0.4" />
              <circle cx="12" cy="12" r="5" stroke="white" strokeWidth="1.5" fill="none" opacity="0.7" />
              <circle cx="12" cy="12" r="2" fill="white" />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-semibold text-foreground">
              Cohort Pulse
            </h1>
            <p className="text-xs text-muted-foreground">
              Customer retention analytics
            </p>
          </div>
        </div>
      </div>
    </header>
  )
}

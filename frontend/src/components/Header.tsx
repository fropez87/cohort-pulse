export function Header() {
  return (
    <header className="border-b border-border bg-white sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center gap-3">
          {/* Logo */}
          <img
            src="/logocp.png"
            alt="Cohort Pulse"
            className="h-9 w-auto"
          />
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

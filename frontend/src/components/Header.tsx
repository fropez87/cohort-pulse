export function Header() {
  return (
    <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center gap-3">
          {/* Logo */}
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-purple-700 flex items-center justify-center shadow-lg shadow-primary/25">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="8" stroke="white" strokeWidth="1.5" fill="none" opacity="0.3" />
              <circle cx="12" cy="12" r="5" stroke="white" strokeWidth="1.5" fill="none" opacity="0.6" />
              <circle cx="12" cy="12" r="2" fill="white" />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-purple-700 bg-clip-text text-transparent">
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

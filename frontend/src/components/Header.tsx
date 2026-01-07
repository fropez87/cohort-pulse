interface HeaderProps {
  onLogoClick?: () => void
}

export function Header({ onLogoClick }: HeaderProps) {
  const handleClick = () => {
    if (onLogoClick) {
      onLogoClick()
    } else {
      window.location.reload()
    }
  }

  return (
    <header className="border-b border-border bg-card sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3 cursor-pointer" onClick={handleClick}>
          <img src="/logocp.png" alt="Cohort Pulse" className="h-8 w-8" />
          <span className="font-semibold text-lg tracking-tight text-foreground">Cohort Pulse</span>
        </div>
      </div>
    </header>
  )
}

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
    <header className="border-b border-border bg-white sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <img
          src="/logocp.png"
          alt="Cohort Pulse"
          className="h-14 w-auto cursor-pointer"
          onClick={handleClick}
        />
      </div>
    </header>
  )
}

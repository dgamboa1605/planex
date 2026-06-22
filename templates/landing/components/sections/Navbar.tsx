import type { NavbarData } from '@/lib/content'
import Container from '@/components/ui/Container'

interface Props { data: NavbarData }

export default function Navbar({ data }: Props) {
  return (
    <header className="sticky top-0 z-50 border-b border-gray-100 bg-white/90 backdrop-blur-sm">
      <Container>
        <div className="flex h-16 items-center justify-between">
          <a href="#" className="text-xl font-bold text-primary">
            {data.logo}
          </a>
          <nav className="hidden items-center gap-6 md:flex">
            {data.links.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-sm font-medium text-gray-600 transition-colors hover:text-primary"
              >
                {link.label}
              </a>
            ))}
          </nav>
        </div>
      </Container>
    </header>
  )
}

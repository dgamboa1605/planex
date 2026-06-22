import type { FooterData } from '@/lib/content'
import Container from '@/components/ui/Container'

interface Props { data: FooterData }

export default function Footer({ data }: Props) {
  return (
    <footer className="bg-gray-900 py-12 text-white">
      <Container>
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <p className="text-sm text-gray-400">{data.copyright}</p>
          {data.links && data.links.length > 0 && (
            <nav className="flex gap-6">
              {data.links.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  className="text-sm text-gray-400 transition-colors hover:text-white"
                >
                  {link.label}
                </a>
              ))}
            </nav>
          )}
        </div>
      </Container>
    </footer>
  )
}

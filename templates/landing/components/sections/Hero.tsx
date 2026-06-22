import type { HeroData } from '@/lib/content'
import { LinkButton } from '@/components/ui/Button'
import Container from '@/components/ui/Container'

interface Props { data: HeroData }

export default function Hero({ data }: Props) {
  return (
    <section className="bg-gradient-to-br from-white to-gray-50 py-24 lg:py-32">
      <Container>
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl">
            {data.title}
          </h1>
          <p className="mt-6 text-lg leading-8 text-gray-600">{data.subtitle}</p>
          <div className="mt-10 flex items-center justify-center">
            <LinkButton href={data.cta.href} size="lg">
              {data.cta.label}
            </LinkButton>
          </div>
        </div>
      </Container>
    </section>
  )
}

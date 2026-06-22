import type { CTASimpleData } from '@/lib/content'
import Container from '@/components/ui/Container'

interface Props { data: CTASimpleData }

export default function CTA({ data }: Props) {
  return (
    <section className="bg-primary py-16 text-white">
      <Container>
        <div className="text-center">
          <h2 className="text-3xl font-bold">{data.headline}</h2>
          {data.subtext && (
            <p className="mx-auto mt-4 max-w-xl text-white/80">{data.subtext}</p>
          )}
          <a
            href={data.buttonHref}
            className="mt-8 inline-flex items-center justify-center rounded-lg bg-white px-8 py-4 text-lg font-semibold text-primary transition-all hover:bg-white/90"
          >
            {data.buttonLabel}
          </a>
        </div>
      </Container>
    </section>
  )
}

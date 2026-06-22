import type { FeaturesData } from '@/lib/content'
import Container from '@/components/ui/Container'

interface Props { data: FeaturesData }

export default function Features({ data }: Props) {
  return (
    <section className="bg-gray-50 py-20">
      <Container>
        {data.headline && (
          <h2 className="mb-12 text-center text-3xl font-bold text-gray-900">{data.headline}</h2>
        )}
        <div className="grid gap-8 sm:grid-cols-2">
          {data.items.map((item, i) => (
            <div key={i} className="flex gap-4">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gray-200">
                <span className="text-sm font-bold text-primary">{i + 1}</span>
              </div>
              <div>
                <h3 className="mb-1 font-semibold text-gray-900">{item.title}</h3>
                <p className="text-sm leading-relaxed text-gray-600">{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </Container>
    </section>
  )
}

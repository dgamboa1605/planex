import type { ServicesData } from '@/lib/content'
import Container from '@/components/ui/Container'

interface Props { data: ServicesData }

export default function Services({ data }: Props) {
  return (
    <section id="servicios" className="bg-white py-20">
      <Container>
        {data.headline && (
          <h2 className="mb-12 text-center text-3xl font-bold text-gray-900">{data.headline}</h2>
        )}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {data.items.map((item, i) => (
            <div
              key={i}
              className="rounded-xl border border-gray-100 bg-gray-50 p-6 transition-all hover:border-primary hover:shadow-sm"
            >
              {item.icon && <div className="mb-4 text-3xl">{item.icon}</div>}
              <h3 className="mb-2 font-semibold text-gray-900">{item.title}</h3>
              <p className="text-sm leading-relaxed text-gray-600">{item.description}</p>
            </div>
          ))}
        </div>
      </Container>
    </section>
  )
}

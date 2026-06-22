import type { CaseStudiesData } from '@/lib/content'
import Container from '@/components/ui/Container'

interface Props { data: CaseStudiesData }

export default function CaseStudies({ data }: Props) {
  return (
    <section id="casos-de-exito" className="bg-white py-20">
      <Container>
        {data.headline && (
          <h2 className="mb-12 text-center text-3xl font-bold text-gray-900">{data.headline}</h2>
        )}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {data.items.map((item, i) => (
            <div key={i} className="rounded-xl border border-gray-200 p-6">
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100">
                <span className="text-lg font-bold text-primary">{item.name[0]}</span>
              </div>
              <h3 className="mb-2 font-semibold text-gray-900">{item.name}</h3>
              {item.description && (
                <p className="text-sm leading-relaxed text-gray-600">{item.description}</p>
              )}
            </div>
          ))}
        </div>
      </Container>
    </section>
  )
}

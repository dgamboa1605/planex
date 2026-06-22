import type { TestimonialsData } from '@/lib/content'
import Container from '@/components/ui/Container'

interface Props { data: TestimonialsData }

export default function Testimonials({ data }: Props) {
  return (
    <section id="testimonios" className="bg-gray-50 py-20">
      <Container>
        {data.headline && (
          <h2 className="mb-12 text-center text-3xl font-bold text-gray-900">{data.headline}</h2>
        )}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {data.items.map((item, i) => (
            <blockquote
              key={i}
              className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm"
            >
              <p className="mb-4 italic leading-relaxed text-gray-600">
                &ldquo;{item.quote}&rdquo;
              </p>
              <footer>
                <p className="font-semibold text-gray-900">{item.author}</p>
                {item.role && <p className="text-sm text-gray-500">{item.role}</p>}
              </footer>
            </blockquote>
          ))}
        </div>
      </Container>
    </section>
  )
}

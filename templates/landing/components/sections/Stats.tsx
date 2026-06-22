import type { StatsData } from '@/lib/content'
import Container from '@/components/ui/Container'

interface Props { data: StatsData }

export default function Stats({ data }: Props) {
  return (
    <section className="bg-primary py-16 text-white">
      <Container>
        <div className="grid grid-cols-2 gap-8 lg:grid-cols-4">
          {data.items.map((item, i) => (
            <div key={i} className="text-center">
              <p className="text-4xl font-bold">{item.value}</p>
              <p className="mt-1 text-sm text-white/80">{item.label}</p>
            </div>
          ))}
        </div>
      </Container>
    </section>
  )
}

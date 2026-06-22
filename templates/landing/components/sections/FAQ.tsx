'use client'

import { useState } from 'react'
import type { FAQData } from '@/lib/content'
import Container from '@/components/ui/Container'

interface Props { data: FAQData }

export default function FAQ({ data }: Props) {
  const [open, setOpen] = useState<number | null>(null)

  return (
    <section className="bg-white py-20">
      <Container>
        {data.headline && (
          <h2 className="mb-12 text-center text-3xl font-bold text-gray-900">{data.headline}</h2>
        )}
        <div className="mx-auto max-w-2xl divide-y divide-gray-200">
          {data.items.map((item, i) => (
            <div key={i}>
              <button
                type="button"
                className="flex w-full items-center justify-between gap-4 py-5 text-left transition-colors hover:text-primary"
                onClick={() => setOpen(open === i ? null : i)}
                aria-expanded={open === i}
              >
                <span className="font-medium text-gray-900">{item.question}</span>
                <span className="shrink-0 text-xl text-primary" aria-hidden="true">
                  {open === i ? '−' : '+'}
                </span>
              </button>
              {open === i && (
                <div className="pb-5 text-sm leading-relaxed text-gray-600">{item.answer}</div>
              )}
            </div>
          ))}
        </div>
      </Container>
    </section>
  )
}

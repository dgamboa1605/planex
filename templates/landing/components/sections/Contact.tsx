'use client'

import { useState } from 'react'
import type { CTAData } from '@/lib/content'
import { Button, LinkButton } from '@/components/ui/Button'
import Container from '@/components/ui/Container'

interface Props { data: CTAData }

export default function Contact({ data }: Props) {
  const [status, setStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle')

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setStatus('sending')
    const formData = new FormData(e.currentTarget)
    const body = Object.fromEntries(formData.entries())
    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      setStatus(res.ok ? 'sent' : 'error')
    } catch {
      setStatus('error')
    }
  }

  return (
    <section id="contacto" className="bg-gray-50 py-20">
      <Container>
        <div className="mx-auto max-w-xl text-center">
          {data.headline && (
            <h2 className="mb-4 text-3xl font-bold text-gray-900">{data.headline}</h2>
          )}
          {data.subtext && <p className="mb-8 text-gray-600">{data.subtext}</p>}

          {/* showForm: false → plain CTA button; showForm: true → contact form */}
          {!data.showForm ? (
            data.buttonHref && (
              <LinkButton href={data.buttonHref} size="lg">
                {data.buttonLabel ?? 'Contáctanos'}
              </LinkButton>
            )
          ) : status === 'sent' ? (
            <p className="font-semibold text-primary">
              ¡Mensaje enviado! Te responderemos pronto.
            </p>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4 text-left">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Nombre</label>
                <input
                  name="name"
                  type="text"
                  required
                  placeholder="Tu nombre"
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Email</label>
                <input
                  name="email"
                  type="email"
                  required
                  placeholder="tu@empresa.com"
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Mensaje</label>
                <textarea
                  name="message"
                  required
                  rows={4}
                  placeholder="Cuéntanos tu reto..."
                  className="w-full resize-none rounded-lg border border-gray-300 px-4 py-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>
              {status === 'error' && (
                <p className="text-sm text-red-500">Hubo un error. Inténtalo de nuevo.</p>
              )}
              <Button type="submit" disabled={status === 'sending'} className="w-full" size="lg">
                {status === 'sending' ? 'Enviando…' : (data.buttonLabel ?? 'Enviar mensaje')}
              </Button>
            </form>
          )}
        </div>
      </Container>
    </section>
  )
}

import type { ComponentType } from 'react'
import Hero from '@/components/sections/Hero'
import Services from '@/components/sections/Services'
import Features from '@/components/sections/Features'
import CaseStudies from '@/components/sections/CaseStudies'
import Testimonials from '@/components/sections/Testimonials'
import Stats from '@/components/sections/Stats'
import FAQ from '@/components/sections/FAQ'
import Contact from '@/components/sections/Contact'
import CTA from '@/components/sections/CTA'

// Maps section type keys (from site.json) → React components.
// Add a new section here when the library grows beyond the MVP 10.
export const SECTION_REGISTRY: Record<string, ComponentType<{ data: any }>> = {
  hero: Hero,
  servicios: Services,
  features: Features,
  'casos-de-exito': CaseStudies,
  testimonios: Testimonials,
  stats: Stats,
  faq: FAQ,
  'cta-contacto': Contact,
  cta: CTA,
}

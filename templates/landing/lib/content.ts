import siteData from '@/content/site.json'

export interface NavLink {
  label: string
  href: string
}

export interface NavbarData {
  logo: string
  links: NavLink[]
}

export interface HeroData {
  title: string
  subtitle: string
  cta: { label: string; href: string }
}

export interface ServicesData {
  headline?: string
  items: { title: string; description: string; icon?: string }[]
}

export interface FeaturesData {
  headline?: string
  items: { title: string; description: string }[]
}

export interface CaseStudiesData {
  headline?: string
  items: { name: string; description?: string }[]
}

export interface TestimonialsData {
  headline?: string
  items: { quote: string; author: string; role?: string }[]
}

export interface StatsData {
  items: { value: string; label: string }[]
}

export interface FAQData {
  headline?: string
  items: { question: string; answer: string }[]
}

export interface CTAData {
  showForm: boolean
  headline?: string
  subtext?: string
  buttonLabel?: string
  buttonHref?: string
}

export interface CTASimpleData {
  headline: string
  subtext?: string
  buttonLabel: string
  buttonHref: string
}

export interface FooterData {
  copyright: string
  links?: NavLink[]
}

export type SectionEntry =
  | { type: 'hero'; data: HeroData }
  | { type: 'servicios'; data: ServicesData }
  | { type: 'features'; data: FeaturesData }
  | { type: 'casos-de-exito'; data: CaseStudiesData }
  | { type: 'testimonios'; data: TestimonialsData }
  | { type: 'stats'; data: StatsData }
  | { type: 'faq'; data: FAQData }
  | { type: 'cta-contacto'; data: CTAData }
  | { type: 'cta'; data: CTASimpleData }

export interface SiteContent {
  theme: { primaryColor: string }
  seo: { title: string; description: string }
  navbar: NavbarData
  footer: FooterData
  sections: SectionEntry[]
}

export async function loadContent(): Promise<SiteContent> {
  return siteData as unknown as SiteContent
}

import type { Metadata } from 'next'
import { loadContent } from '@/lib/content'
import SectionRenderer from '@/components/SectionRenderer'
import Navbar from '@/components/sections/Navbar'
import Footer from '@/components/sections/Footer'

export async function generateMetadata(): Promise<Metadata> {
  const content = await loadContent()
  return {
    title: content.seo.title,
    description: content.seo.description,
  }
}

export default async function Home() {
  const content = await loadContent()

  return (
    <>
      {/* Inject primaryColor from site.json into the CSS custom property */}
      <style
        dangerouslySetInnerHTML={{
          __html: `:root { --color-primary: ${content.theme.primaryColor}; }`,
        }}
      />
      <Navbar data={content.navbar} />
      <main>
        <SectionRenderer sections={content.sections} />
      </main>
      <Footer data={content.footer} />
    </>
  )
}

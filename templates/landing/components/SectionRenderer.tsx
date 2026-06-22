import type { SectionEntry } from '@/lib/content'
import { SECTION_REGISTRY } from '@/lib/sections'

interface Props {
  sections: SectionEntry[]
}

export default function SectionRenderer({ sections }: Props) {
  return (
    <>
      {sections.map((section, index) => {
        const Component = SECTION_REGISTRY[section.type]
        if (!Component) {
          console.warn(`[SectionRenderer] Unknown section type: "${section.type}"`)
          return null
        }
        return <Component key={`${section.type}-${index}`} data={section.data} />
      })}
    </>
  )
}

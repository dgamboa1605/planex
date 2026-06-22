import { AnchorHTMLAttributes, ButtonHTMLAttributes, ReactNode } from 'react'

type Variant = 'primary' | 'outline' | 'ghost'
type Size = 'sm' | 'md' | 'lg'

const BASE =
  'inline-flex items-center justify-center rounded-lg font-semibold transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-primary'

const VARIANTS: Record<Variant, string> = {
  primary: 'bg-primary text-white hover:opacity-90 active:opacity-80',
  outline: 'border-2 border-primary text-primary hover:bg-primary hover:text-white',
  ghost: 'text-primary hover:bg-gray-100',
}

const SIZES: Record<Size, string> = {
  sm: 'px-4 py-2 text-sm',
  md: 'px-6 py-3 text-base',
  lg: 'px-8 py-4 text-lg',
}

function classes(variant: Variant, size: Size, extra = '') {
  return [BASE, VARIANTS[variant], SIZES[size], extra].filter(Boolean).join(' ')
}

type ButtonProps = { variant?: Variant; size?: Size } & ButtonHTMLAttributes<HTMLButtonElement>

type LinkProps = {
  variant?: Variant
  size?: Size
  href: string
  children: ReactNode
} & AnchorHTMLAttributes<HTMLAnchorElement>

export function Button({ variant = 'primary', size = 'md', className = '', ...props }: ButtonProps) {
  return <button className={classes(variant, size, className)} {...props} />
}

export function LinkButton({
  variant = 'primary',
  size = 'md',
  href,
  className = '',
  children,
  ...props
}: LinkProps) {
  return (
    <a href={href} className={classes(variant, size, className)} {...props}>
      {children}
    </a>
  )
}

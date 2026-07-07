import { cn } from '@/lib/utils'

interface ProgressProps {
  value: number
  className?: string
  variant?: 'default' | 'success' | 'warning'
}

export function Progress({ value, className, variant = 'default' }: ProgressProps) {
  return (
    <div
      className={cn(
        'w-full h-2 rounded-full bg-muted overflow-hidden',
        className
      )}
    >
      <div
        className={cn(
          'h-full rounded-full transition-all duration-500 ease-out',
          {
            'bg-foreground': variant === 'default',
            'bg-emerald-500': variant === 'success',
            'bg-amber-500': variant === 'warning',
          }
        )}
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  )
}

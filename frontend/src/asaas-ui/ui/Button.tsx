import type { ButtonHTMLAttributes } from 'react';
import { cx } from '../lib/cx';
import { Icon, type IconName } from './Icon';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'glass' | 'ghost' | 'danger';
  size?: 'md' | 'sm';
  icon?: IconName;
  /** Explicitly make this button a compact icon-only square button */
  iconOnly?: boolean;
  /** Label text of the button. Displayed as text if children is omitted, or as aria-label/title if iconOnly */
  label?: string;
  loading?: boolean;
}

export function Button({
  variant = 'glass',
  size = 'md',
  icon,
  iconOnly,
  label,
  loading,
  className,
  children,
  disabled,
  type = 'button',
  ...props
}: ButtonProps) {
  // If iconOnly is explicitly true, or there's an icon with no text content at all
  const isIconBtn = Boolean(iconOnly || (icon && !children && !label));
  const visibleContent = children !== undefined ? children : (iconOnly ? null : label);

  return (
    <button
      type={type}
      className={cx(
        'btn',
        `btn--${variant}`,
        size === 'sm' && 'btn--sm',
        isIconBtn && 'btn--icon',
        className
      )}
      disabled={disabled || loading}
      aria-label={label || (typeof children === 'string' ? children : undefined)}
      title={label || (typeof children === 'string' ? children : undefined)}
      {...props}
    >
      {icon && <Icon name={icon} className="btn-icon-svg" />}
      {loading ? 'جارٍ المعالجة…' : visibleContent}
    </button>
  );
}

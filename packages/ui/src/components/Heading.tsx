import { cn } from "@repo/lib";
import { VariantProps, cva } from "class-variance-authority";
import { HTMLAttributes } from "react";

const headingVariants = cva("font-bold leading-tight tracking-tighter", {
  variants: {
    size: {
      1: "text-4xl md:text-5xl lg:text-6xl",
      2: "text-3xl md:text-4xl lg:text-5xl",
      3: "text-2xl md:text-3xl lg:text-4xl",
      4: "text-xl md:text-2xl lg:text-3xl",
      5: "text-lg md:text-xl lg:text-2xl",
      6: "text-base md:text-lg lg:text-xl",
    },
  },
  defaultVariants: {
    size: 1,
  },
});

interface HeadingProps
  extends HTMLAttributes<HTMLHeadingElement>,
    VariantProps<typeof headingVariants> {
  as?: "h1" | "h2" | "h3" | "h4" | "h5" | "h6";
  size?: 1 | 2 | 3 | 4 | 5 | 6;
}

export function Heading({
  className,
  size,
  as: Component = "h1",
  ...props
}: HeadingProps) {
  return (
    <Component
      className={cn(headingVariants({ size, className }))}
      {...props}
    />
  );
}

# Implementation — shadcn/ui + Tailwind CSS

Turning tokens into shipped UI: shadcn/ui (Radix UI primitives) setup, component
patterns, dark mode, responsive layout, theme customization, and accessibility
rules.

**Applies to** React-based frameworks (Next.js, Vite, Remix, Astro).

**Skip when** the project uses Vue.js (use Vuetify/Nuxt UI patterns), a
mobile-native stack (React Native / Flutter), or non-Tailwind CSS (Bootstrap,
plain CSS).

---

## Stack

| Layer | Technology | Role |
|-------|-----------|------|
| Components | shadcn/ui (Radix UI primitives) | Accessible, composable components |
| Styling | Tailwind CSS | Utility-first, design tokens |
| Types | TypeScript | Full type safety |

**shadcn/ui model:** Components are copied into your codebase
(`components/ui/`), not imported from npm. You own the code.

---

## Setup

### shadcn/ui + Tailwind

```bash
npx shadcn@latest init
```

CLI prompts for framework, TypeScript, paths, and theme. Configures both
shadcn/ui and Tailwind.

```bash
# Add components
npx shadcn@latest add button card dialog form input select table
```

### Tailwind-Only (Vite)

```bash
npm install -D tailwindcss @tailwindcss/vite
```

```javascript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'
export default { plugins: [tailwindcss()] }
```

```css
/* src/index.css */
@import "tailwindcss";
```

---

## Component Patterns

### Form with Validation (React Hook Form + Zod)

```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const schema = z.object({
  email: z.string().email("Valid email required"),
  password: z.string().min(8, "Minimum 8 characters"),
})

export function LoginForm() {
  const form = useForm({ resolver: zodResolver(schema) })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField control={form.control} name="email" render={({ field }) => (
          <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl>
              <Input type="email" placeholder="you@example.com" {...field} />
            </FormControl>
            <FormMessage />  {/* auto error display */}
          </FormItem>
        )} />
        <Button type="submit" className="w-full">Sign In</Button>
      </form>
    </Form>
  )
}
```

### Responsive Grid Layout

```tsx
<div className="min-h-screen bg-background">
  <div className="container mx-auto px-4 py-8">
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <Card className="hover:shadow-lg transition-shadow">
        <CardHeader>
          <CardTitle>Analytics</CardTitle>
          <CardDescription>View your key metrics</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">Track performance</p>
          <Button variant="outline" className="w-full">View Details</Button>
        </CardContent>
      </Card>
    </div>
  </div>
</div>
```

### Dialog / Modal

```tsx
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"

<Dialog>
  <DialogTrigger asChild>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent className="sm:max-w-[425px]">
    <DialogHeader>
      <DialogTitle>Edit Profile</DialogTitle>
    </DialogHeader>
    <div className="grid gap-4 py-4">
      {/* form content */}
    </div>
  </DialogContent>
</Dialog>
```

### Data Table

```tsx
import { DataTable } from "@/components/ui/data-table"
import { ColumnDef } from "@tanstack/react-table"

const columns: ColumnDef<User>[] = [
  { accessorKey: "name", header: "Name" },
  { accessorKey: "email", header: "Email" },
  {
    id: "actions",
    cell: ({ row }) => <DropdownMenuActions row={row.original} />,
  },
]

<DataTable columns={columns} data={users} />
```

---

## Dark Mode

### Setup with next-themes

```bash
npm install next-themes
```

```tsx
// providers.tsx
import { ThemeProvider } from "next-themes"

export function Providers({ children }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </ThemeProvider>
  )
}
```

### Theme Toggle

```tsx
import { useTheme } from "next-themes"
import { Moon, Sun } from "lucide-react"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  return (
    <Button variant="ghost" size="icon" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
      <Sun className="h-5 w-5 rotate-0 scale-100 dark:-rotate-90 dark:scale-0 transition-all" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 dark:rotate-0 dark:scale-100 transition-all" />
    </Button>
  )
}
```

### Dark Utility Classes

```tsx
// Always pair light and dark variants
<div className="bg-white dark:bg-gray-900">
  <h1 className="text-gray-900 dark:text-gray-100">Title</h1>
  <p className="text-gray-600 dark:text-gray-400">Subtitle</p>
  <Card className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
    ...
  </Card>
</div>
```

---

## Tailwind Responsive Breakpoints

| Prefix | Min-width | Typical use |
|--------|-----------|-------------|
| (none) | 0px | Mobile default |
| `sm:` | 640px | Small tablet |
| `md:` | 768px | Tablet |
| `lg:` | 1024px | Desktop |
| `xl:` | 1280px | Large desktop |
| `2xl:` | 1536px | Wide screens |

```tsx
// Mobile-first pattern
<div className="flex flex-col md:flex-row gap-4">
  <aside className="w-full md:w-64">Sidebar</aside>
  <main className="flex-1">Content</main>
</div>
```

---

## Tailwind Theme Customization

```javascript
// tailwind.config.js
export default {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        border: "hsl(var(--border))",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
}
```

The `hsl(var(--token))` values come from the semantic layer in
`references/tokens.md` — define tokens there first, wire them here.

---

## Accessibility Rules

- **shadcn/ui** components include ARIA roles/attributes via Radix UI primitives
- Always use semantic HTML (`button`, `nav`, `main`, `header`, `section`)
- Focus rings: shadcn/ui includes focus-visible styles — do not remove them
- Icon-only buttons: always add `aria-label`

```tsx
// Accessible icon-only button
<Button variant="ghost" size="icon" aria-label="Delete item">
  <Trash2 className="h-4 w-4" />
</Button>

// Screen reader text
<span className="sr-only">Loading...</span>
```

---

## Component State Classes

```tsx
// Hover
className="hover:bg-accent hover:text-accent-foreground"

// Active / pressed
className="active:scale-95 transition-transform"

// Disabled
className="disabled:pointer-events-none disabled:opacity-50"

// Focus
className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"

// Loading (with spinner)
<Button disabled={isLoading}>
  {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
  {isLoading ? "Saving..." : "Save"}
</Button>
```

---

## shadcn/ui Component Reference

| Component | Install command | Use for |
|-----------|----------------|---------|
| Button | `add button` | Primary/secondary actions |
| Input | `add input` | Text inputs |
| Form | `add form` | Form with validation |
| Select | `add select` | Dropdown selection |
| Dialog | `add dialog` | Modal dialogs |
| Sheet | `add sheet` | Slide-over panels |
| Card | `add card` | Content containers |
| Table | `add table` | Data display |
| DataTable | `add data-table` | Sortable/filterable tables |
| Tabs | `add tabs` | Tab navigation |
| Dropdown | `add dropdown-menu` | Context menus |
| Command | `add command` | Command palette / search |
| Toast | `add toast` | Notifications |
| Skeleton | `add skeleton` | Loading placeholders |
| Badge | `add badge` | Status indicators |
| Avatar | `add avatar` | User images |
| Alert | `add alert` | Info/error messages |
| Progress | `add progress` | Progress bars |
| Separator | `add separator` | Visual dividers |

---

## Best Practices

1. **Composition over props** — Use `cn()` and slot pattern for component variants
2. **Mobile-first** — Start with mobile styles, add responsive variants
3. **Semantic tokens** — Never hardcode hex values; use CSS variables from the token layer
4. **Dark mode parity** — Every themed element needs a dark: variant
5. **No dynamic class names** — Tailwind purges unknown classes; full class names only
6. **TypeScript strict** — No `any` in component props; use proper TS types
7. **Lucide icons** — Use Lucide React (included with shadcn/ui) for consistent icons

```tsx
// CORRECT — full class name
const variants = { primary: "bg-primary text-primary-foreground" }

// WRONG — dynamic class construction (gets purged by Tailwind)
const color = "primary"
const className = `bg-${color} text-${color}-foreground`
```

---

## Deeper implementation references

| File | Content |
|------|---------|
| `references/shadcn-components.md` | Full component catalog with TSX examples: Button, Form+Zod, Select, Dialog, Table, Command, and 20+ more |
| `references/shadcn-accessibility.md` | Radix UI ARIA foundation, keyboard nav, focus management, screen reader support, testing checklist |
| `references/shadcn-theming.md` | Dark mode (next-themes/Vite), CSS variable system, HSL format, multiple themes, radius, base presets |
| `references/tailwind-utilities.md` | Comprehensive utility class reference: layout, spacing, typography, colors, borders, shadows |
| `references/tailwind-responsive.md` | Mobile-first breakpoints, responsive patterns, container queries, max-width queries |
| `references/tailwind-customization.md` | @theme directive, custom utilities, @apply, plugins, complete tailwind.config.ts example |
| `references/canvas-design-system.md` | Canvas/poster visual design philosophy and composition (uses the bundled `canvas-fonts/`) |

## Implementation scripts

| File | Purpose |
|------|---------|
| `scripts/shadcn_add.py` | Programmatic shadcn/ui component installer with dependency handling |
| `scripts/tailwind_config_gen.py` | Tailwind config generator with custom theme configuration |

Both have unit tests under `scripts/tests/`.

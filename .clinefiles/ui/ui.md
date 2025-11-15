# UI Component Guidelines

This document contains critical information about UI components and common issues to avoid.

## Critical: Tailwind CSS Version Compatibility

### The Issue

Our project uses **Tailwind CSS v3.4.18**, but some shadcn/ui components (particularly the Sidebar component) may be generated using **Tailwind v4 syntax**, which is incompatible.

### Symptoms

When Tailwind v4 syntax is used in a v3 project, CSS custom properties don't work correctly, resulting in:

1. **Components appear broken** - Missing widths, heights, or positioning
2. **Transparent backgrounds** - Background colors don't apply
3. **Layout issues** - Elements overlap or don't respect spacing
4. **Content extending incorrectly** - Gap elements have no width

### How to Identify the Problem

Look for this v4 syntax pattern in component files:

```typescript
// ❌ WRONG - Tailwind v4 syntax (incompatible with v3)
className="w-(--sidebar-width)"
className="h-(--header-height)"
className="max-w-(--skeleton-width)"
```

### The Fix

Convert all Tailwind v4 arbitrary value syntax to v3 format:

```typescript
// ✅ CORRECT - Tailwind v3 syntax
className="w-[var(--sidebar-width)]"
className="h-[var(--header-height)]"
className="max-w-[var(--skeleton-width)]"
```

**Pattern to follow:**
- v4: `property-(--css-variable)`
- v3: `property-[var(--css-variable)]`

### Example: Sidebar Component Fix

When installing the shadcn Sidebar component, check `components/ui/sidebar.tsx` for v4 syntax:

**Before (v4 - broken):**
```typescript
<div className="w-(--sidebar-width)">
```

**After (v3 - working):**
```typescript
<div className="w-[var(--sidebar-width)]">
```

### Calc Expressions

For calculated values, also use v3 syntax:

**Before (v4):**
```typescript
className="w-[calc(+(--sidebar-width-icon)+(--spacing(4)))]"
```

**After (v3):**
```typescript
className="w-[calc(var(--sidebar-width-icon)+1rem+2px)]"
```

**Note:** The `--spacing(4)` syntax doesn't exist in v3. Convert to explicit values like `1rem` or `16px`.

## Component Installation Checklist

When installing new shadcn/ui components or blocks:

1. **Install the component:**
   ```bash
   npx shadcn@latest add <component-name>
   ```

2. **Immediately check for v4 syntax:**
   ```bash
   # Search for v4 patterns in the new component
   grep -r "className.*-(" components/ui/
   ```

3. **Convert any v4 syntax to v3:**
   - Look for `property-(--variable)` patterns
   - Replace with `property-[var(--variable)]`
   - Replace calc expressions like `+(--spacing(N))` with explicit values

4. **Test the component:**
   - Start dev server
   - Verify component renders correctly
   - Check for missing styles or layout issues

## Sidebar-Specific Guidelines

### Collapsible Modes

The Sidebar component supports three collapsible modes:

**`icon` (Recommended for dashboards):**
```typescript
<Sidebar collapsible="icon">
```
- Sidebar pushes content to the right
- Collapses to icon bar instead of hiding
- Gap element maintains space for sidebar
- Best for: Desktop applications with persistent navigation

**`offcanvas` (⚠️ Can cause layout issues):**
```typescript
<Sidebar collapsible="offcanvas">
```
- Sidebar overlays content like a mobile drawer
- Content extends full-width underneath
- Gap element width set to 0
- Best for: Mobile-only or temporary drawers
- **Note:** This mode can cause text overlap if used incorrectly

**`none`:**
```typescript
<Sidebar collapsible="none">
```
- Sidebar always visible, never collapses
- Best for: Always-on navigation

### Layout Structure

Always use this structure for sidebar layouts:

```typescript
<SidebarProvider>
  <AppSidebar collapsible="icon" />
  <SidebarInset>
    <SiteHeader />
    <main className="flex flex-1 flex-col gap-4 p-4">
      {children}
    </main>
  </SidebarInset>
</SidebarProvider>
```

**Key points:**
- `SidebarProvider` wraps everything
- `AppSidebar` comes first
- `SidebarInset` wraps main content
- Gap element is automatically inserted

## Navigation Components

### Adding Links to Navigation

Navigation components must use Next.js Link for proper routing:

**❌ WRONG - Missing Link:**
```typescript
<SidebarMenuButton>
  {item.icon && <item.icon />}
  <span>{item.title}</span>
</SidebarMenuButton>
```

**✅ CORRECT - With Link:**
```typescript
<SidebarMenuButton asChild>
  <Link href={item.url}>
    {item.icon && <item.icon />}
    <span>{item.title}</span>
  </Link>
</SidebarMenuButton>
```

**Required changes:**
1. Import Link: `import Link from "next/link"`
2. Add `asChild` prop to button component
3. Wrap content in `<Link href={url}>`

## Common Issues and Solutions

### Issue: Sidebar has transparent background

**Cause:** Tailwind v4 syntax preventing CSS custom properties from working

**Solution:** Convert all `--(variable)` syntax to `[var(--variable)]` in `components/ui/sidebar.tsx`

### Issue: Content extends under sidebar

**Cause:** Using `collapsible="offcanvas"` mode incorrectly

**Solution:** Change to `collapsible="icon"` in `components/app-sidebar.tsx`

### Issue: Navigation buttons don't work

**Cause:** Missing Next.js Link wrapper

**Solution:** Update `components/nav-main.tsx` and `components/nav-secondary.tsx` to use Link

## Best Practices

1. **Always verify Tailwind syntax** after installing new components
2. **Use `collapsible="icon"`** for dashboard layouts
3. **Include Link components** in all navigation items
4. **Test immediately** after component installation
5. **Check for console errors** related to CSS custom properties
6. **Document any workarounds** needed for specific components

## Reference Files

When working with UI components, refer to these docs:

- `.clinerules/ui/shadcn-components.md` - Individual component reference
- `.clinerules/ui/shadcn-blocks.md` - Pre-built blocks and layouts
- `.clinerules/ui/supabase-blocks.md` - Supabase-integrated components
- `.clinerules/ui/reactflow-patterns.md` - Node-based visualizations

## Version Information

- **Project Tailwind CSS:** v3.4.18
- **shadcn/ui:** Uses latest component versions
- **Important:** Always convert v4 syntax to v3 when installing components

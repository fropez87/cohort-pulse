# Design Guide

Reference this skill whenever building any UI component to ensure a modern, professional look.

## Core Principles

1. **Clean and minimal** - Lots of white space, not cluttered
2. **Neutral color palette** - Grays and off-whites as base, ONE accent color used sparingly
3. **NO generic purple/blue gradients**
4. **8px grid system** - Use consistent spacing: 8, 16, 24, 32, 48, 64px
5. **Typography hierarchy** - Clear hierarchy, 16px minimum for body text, max 2 fonts
6. **Subtle shadows** - Not heavy or overdone
7. **Selective rounding** - Rounded corners where appropriate, not everywhere
8. **Clear interactive states** - Hover, active, disabled states
9. **Mobile-first** - Design for mobile first, then scale up

## Color Guidelines

```
Base colors:
- Background: #FFFFFF, #FAFAFA, #F5F5F5
- Text primary: #1A1A1A, #2D2D2D
- Text secondary: #6B7280, #9CA3AF
- Borders: #E5E7EB, #D1D5DB

Accent: Pick ONE and use sparingly
- For actions, links, highlights only
- Don't use for backgrounds or large areas
```

## Spacing Scale (8px grid)

```
4px   - tight (icons, inline elements)
8px   - compact (between related items)
16px  - default (form fields, list items)
24px  - comfortable (card padding, sections)
32px  - spacious (between sections)
48px  - generous (page sections)
64px  - expansive (hero sections, major breaks)
```

## Typography

```
Headings:
- H1: 32-40px, font-weight 700
- H2: 24-28px, font-weight 600
- H3: 20px, font-weight 600
- H4: 18px, font-weight 500

Body: 16px minimum, line-height 1.5-1.6
Small text: 14px (captions, metadata)
Never go below 12px
```

## Component Patterns

### Buttons
```css
/* Good */
padding: 12px 24px;
border-radius: 6px;
font-weight: 500;
box-shadow: 0 1px 2px rgba(0,0,0,0.05);
transition: all 150ms ease;

/* Hover: darken background slightly, subtle lift */
/* Active: slightly darker, no lift */
/* Disabled: 50% opacity, no pointer events */

/* Bad */
- Gradients
- Heavy drop shadows
- Tiny padding
- No hover state
```

### Cards
```css
/* Good - pick ONE */
Option A: border: 1px solid #E5E7EB;
Option B: box-shadow: 0 1px 3px rgba(0,0,0,0.1);

padding: 24px;
border-radius: 8px;
background: #FFFFFF;

/* Bad */
- Border AND heavy shadow
- Gradient backgrounds
- Inconsistent padding
```

### Forms
```css
/* Good */
label: 14px, font-weight 500, margin-bottom 6px
input: 16px, padding 12px 16px, border-radius 6px
error: red-600 text below field, red border on input
spacing: 24px between fields

/* Bad */
- Placeholder as label
- No error states
- Cramped spacing
- Tiny inputs
```

### Tables/Data
```css
/* Good */
header: font-weight 500, background #F9FAFB
cells: padding 12px 16px
borders: subtle horizontal lines only OR zebra striping, not both
hover: subtle background change on rows

/* Bad */
- Grid lines everywhere
- No visual hierarchy
- Cramped cells
```

## Shadows Scale

```css
/* Subtle (default for cards) */
box-shadow: 0 1px 3px rgba(0,0,0,0.1);

/* Medium (dropdowns, popovers) */
box-shadow: 0 4px 6px rgba(0,0,0,0.1);

/* Elevated (modals) */
box-shadow: 0 10px 25px rgba(0,0,0,0.15);

/* Never use harsh black shadows */
```

## Border Radius Scale

```css
4px  - buttons, inputs, small elements
8px  - cards, containers
12px - modals, large containers
full - avatars, badges, pills
```

## Do's and Don'ts

### Do
- Use whitespace generously
- Maintain consistent alignment
- Create clear visual hierarchy
- Test on mobile
- Use subtle animations (150-300ms)

### Don't
- Cram elements together
- Use more than 3 font sizes per view
- Add decorative elements without purpose
- Use rainbow/gradient backgrounds
- Make everything the same visual weight

# Code with TLP — Background Image Style Guide

## Overview

All lesson background images share a single cohesive visual language so the platform feels unified across every course and subject. Images are always **backgrounds behind readable text**, so they must stay visually quiet, leave generous open space, and never compete with the content.

---

## Core Style

**Modern, clean, abstract tech illustration** — semi-flat geometric shapes, soft gradient meshes, and sparse symbolic motifs. Think tasteful editorial illustration rather than photorealism or loud infographics. Shapes are elegant and purposeful, not cluttered.

---

## Composition Rules

| Rule | Detail |
|---|---|
| Focal elements | Pushed to **corners or edges** (one strong corner anchor, or a gentle curve along one side). The **center 60% of the canvas is mostly empty** for text overlay. |
| Visual weight | Light-to-medium — no dense textures or busy gradients in the center. |
| Contrast | Low-to-medium. Shapes should read as subtle. Never full black on white in the center area. |
| Aspect ratio | **16:9 landscape** for every image. |
| Text / UI | **No text, no words, no letters, no numbers, no UI chrome, no logos, no watermarks anywhere in the image.** |
| Depth | One or two very soft, blurred secondary shapes behind the main motif to create slight depth without noise. |

---

## Light Theme vs Dark Theme

Every prompt describes the **light-theme variant** (pale/white/cream background, soft-tinted shapes). Add a one-line dark-theme note at the end of each prompt: swap the background to a very dark near-black version of the subject color, lighten the shapes slightly, and keep contrast low.

---

## Per-Subject Color Palettes

Each subject has an anchor hex color. Build palettes from that anchor plus a lighter tint (+60% lightness), a softer mid-tone (+30%), and a neutral off-white or cream base for the background field.

| Subject | Slug | Anchor Hex | Use |
|---|---|---|---|
| Computer Science Foundations | foundations | `#8b5cf6` | Violet-purple |
| Algorithms & Data Structures | algorithms | `#3b82f6` | Bright blue |
| Programming | programming | `#06b6d4` | Cyan-teal |
| Systems | systems | `#ef4444` | Coral-red |
| Theory of Computation | theory | `#ec4899` | Pink-rose |
| Software Engineering | software-engineering | `#14b8a6` | Teal-green |
| Artificial Intelligence | artificial-intelligence | `#f97316` | Warm orange |
| Web Development | web-development | `#10b981` | Emerald-green |
| Databases | databases | `#f59e0b` | Amber-gold |

---

## Prompt Writing Checklist

Each prompt paragraph must include:

1. Concrete subject metaphor or visual (what the image depicts)
2. Composition description (where elements sit, where negative space lives)
3. Color palette reference (anchor hex + descriptive names)
4. Mood and lighting
5. Art style descriptor
6. "16:9 aspect ratio"
7. Explicit no-text instruction: "no text, no words, no letters, no UI, no watermark"
8. A one-line dark-theme variant note

Target length: 60–110 words per prompt.

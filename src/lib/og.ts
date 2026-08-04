import fs from 'node:fs';
import path from 'node:path';
import satori from 'satori';
import { Resvg } from '@resvg/resvg-js';

/**
 * Build-time Open Graph card rendering.
 *
 * Satori turns a small element tree into SVG, resvg rasterises it. Fonts have
 * to be handed over as binary — it reads ttf/otf/woff but not woff2, which is
 * why this pulls from @fontsource/* (static .woff) rather than the variable
 * packages the site itself loads.
 */

// Resolved against the project root, not import.meta.url: this module gets
// bundled into dist/ for the build, so a relative URL would point at the wrong
// tree. `npm run build` always runs from the root.
const font = (file: string) => fs.readFileSync(path.join(process.cwd(), file));

const FONTS = [
  {
    name: 'Inter Tight',
    data: font('node_modules/@fontsource/inter-tight/files/inter-tight-latin-700-normal.woff'),
    weight: 700 as const,
    style: 'normal' as const,
  },
  {
    name: 'IBM Plex Mono',
    data: font('node_modules/@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff'),
    weight: 400 as const,
    style: 'normal' as const,
  },
];

// The card commits to the dark ground — social clients show it against their
// own chrome, so there is no theme to follow.
const INK = '#e8eae6';
const MUTED = '#a2a8a2';
const BG = '#141618';
const HAIRLINE = '#2b2e31';

/** The site's dot-mark, rebuilt as plain divs since satori takes no SVG. */
function logoMark() {
  const dots = [
    [0, 2, 0.95], [0, 1, 0.7],
    [1, 2, 0.95], [1, 1, 0.7], [1, 0, 0.5],
    [2, 2, 0.95], [2, 1, 0.7], [2, 0, 0.5],
  ];
  return {
    type: 'div',
    props: {
      style: { display: 'flex', position: 'relative', width: 34, height: 34 },
      children: dots.map(([col, row, opacity]) => ({
        type: 'div',
        props: {
          style: {
            position: 'absolute',
            left: col * 13,
            top: row * 13,
            width: 8,
            height: 8,
            borderRadius: 4,
            background: INK,
            opacity,
          },
        },
      })),
    },
  };
}

function row(children: unknown[], style: Record<string, unknown> = {}) {
  return { type: 'div', props: { style: { display: 'flex', alignItems: 'center', ...style }, children } };
}

function text(value: string, style: Record<string, unknown>) {
  return { type: 'div', props: { style: { display: 'flex', ...style }, children: value } };
}

export interface CardOptions {
  title: string;
  /** small mono line above the title — a date, or a section name */
  eyebrow?: string;
  /** accent bar down the left edge */
  accent?: string;
}

export async function renderCard({ title, eyebrow, accent = '#fc4c02' }: CardOptions): Promise<Buffer> {
  const tree = {
    type: 'div',
    props: {
      style: {
        display: 'flex',
        width: '100%',
        height: '100%',
        background: BG,
        color: INK,
        fontFamily: 'Inter Tight',
        borderLeft: `14px solid ${accent}`,
      },
      children: [
        {
          type: 'div',
          props: {
            style: {
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              padding: '64px 72px',
              width: '100%',
            },
            children: [
              eyebrow
                ? text(eyebrow.toUpperCase(), {
                    fontFamily: 'IBM Plex Mono',
                    fontSize: 24,
                    letterSpacing: 3,
                    color: MUTED,
                  })
                : text('', {}),
              text(title, {
                fontSize: title.length > 78 ? 60 : title.length > 46 ? 72 : 84,
                lineHeight: 1.1,
                letterSpacing: -2,
                // satori has no text-wrap:balance; clamp instead so a long
                // title cannot push the footer off the card
                maxHeight: 330,
                overflow: 'hidden',
              }),
              row(
                [
                  logoMark(),
                  text('fabriziogf.github.io', {
                    fontFamily: 'IBM Plex Mono',
                    fontSize: 24,
                    color: MUTED,
                    marginLeft: 18,
                  }),
                ],
                { borderTop: `1px solid ${HAIRLINE}`, paddingTop: 28 }
              ),
            ],
          },
        },
      ],
    },
  };

  const svg = await satori(tree as never, { width: 1200, height: 630, fonts: FONTS });
  return new Resvg(svg).render().asPng();
}

import { getCollection, type CollectionEntry } from 'astro:content';

export type Post = CollectionEntry<'posts'>;

const FILENAME = /^(\d{4})-(\d{2})-(\d{2})-(.+)$/;

/** Jekyll filename convention: YYYY-MM-DD-Slug → { date, slug }. */
export function parseId(id: string): { date: Date; slug: string } {
  const m = id.match(FILENAME);
  if (!m) throw new Error(`Post filename does not follow YYYY-MM-DD-slug: ${id}`);
  const [, y, mo, d, slug] = m;
  return { date: new Date(Number(y), Number(mo) - 1, Number(d)), slug };
}

/** All posts, newest first. */
export async function sortedPosts(): Promise<Post[]> {
  const posts = await getCollection('posts');
  return posts.sort((a, b) => parseId(b.id).date.getTime() - parseId(a.id).date.getTime());
}

export function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

export function isoDate(date: Date): string {
  const p = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${p(date.getMonth() + 1)}-${p(date.getDate())}`;
}

/* ── Multi-part series ──────────────────────────────────────────────────────
 * Membership comes from the filename: `..._partN` groups on the slug prefix.
 * Nothing to maintain in front matter — adding `..._part11.md` picks it up.
 */

const SERIES_SLUG = /^(.+)_part(\d+)$/i;
/** "Series Name — Part 3: Subtitle" → captures the name and the subtitle. */
const SERIES_TITLE = /^(.*?)\s*[—–-]\s*Part\s*\d+\s*:?\s*(.*)$/i;

export interface SeriesPart {
  slug: string;
  part: number;
  title: string;
  /** the part's own subtitle, falling back to the full title */
  label: string;
  current: boolean;
}

export interface Series {
  /** name shared by every part, e.g. "Building a World Cup Prediction Model" */
  name: string;
  parts: SeriesPart[];
  index: number;
  previous?: SeriesPart;
  next?: SeriesPart;
}

/** Series key and part number for a slug, or null if it isn't part of one. */
export function parseSeries(slug: string): { key: string; part: number } | null {
  const m = slug.match(SERIES_SLUG);
  return m ? { key: m[1], part: Number(m[2]) } : null;
}

/**
 * The series `post` belongs to, ordered by part number rather than date so
 * two parts published the same day still sort correctly. Returns null for
 * standalone posts and for a series that never got a second part.
 */
export async function seriesFor(post: Post): Promise<Series | null> {
  const here = parseSeries(parseId(post.id).slug);
  if (!here) return null;

  const parts: SeriesPart[] = [];
  let name = here.key.replace(/_/g, ' ');

  for (const entry of await getCollection('posts')) {
    const { slug } = parseId(entry.id);
    const info = parseSeries(slug);
    if (info?.key !== here.key) continue;

    const title = entry.data.title;
    const m = title.match(SERIES_TITLE);
    if (m?.[1]) name = m[1];

    parts.push({
      slug,
      part: info.part,
      title,
      label: m?.[2]?.trim() || title,
      current: info.part === here.part,
    });
  }

  if (parts.length < 2) return null;
  parts.sort((a, b) => a.part - b.part);

  const index = parts.findIndex((p) => p.current);
  return { name, parts, index, previous: parts[index - 1], next: parts[index + 1] };
}

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

/* ── Series ─────────────────────────────────────────────────────────────────
 * Membership comes from the filename, so there is nothing to maintain in
 * front matter. Two shapes:
 *
 *   `..._partN`             a numbered series, ordered by part number, and
 *                           shown with a full index of every part
 *   `..._training_analysis` the monthly run, ordered by date, prev/next only
 */

const SERIES_SLUG = /^(.+)_part(\d+)$/i;
/** "Series Name — Part 3: Subtitle" → captures the name and the subtitle. */
const SERIES_TITLE = /^(.*?)\s*[—–-]\s*Part\s*\d+\s*:?\s*(.*)$/i;

const ANALYSIS_SLUG = /_training_analysis$/i;
/** "January 2026 Training Analysis" → captures the month and year. */
const ANALYSIS_TITLE = /^(.*?)\s*Training Analysis$/i;

export interface SeriesPart {
  slug: string;
  title: string;
  /** long form, used in the index list */
  label: string;
  /** short form, used on the prev/next links */
  navLabel: string;
  current: boolean;
}

export interface Series {
  /** name shared by every entry, e.g. "Building a World Cup Prediction Model" */
  name: string;
  parts: SeriesPart[];
  index: number;
  previous?: SeriesPart;
  next?: SeriesPart;
  /** numbered series list every part; the monthly run would be endless */
  showIndex: boolean;
  /** "Part 6 of 10" — only where a fixed position means something */
  counter?: string;
}

/** Series key and part number for a slug, or null if it isn't part of one. */
export function parseSeries(slug: string): { key: string; part: number } | null {
  const m = slug.match(SERIES_SLUG);
  return m ? { key: m[1], part: Number(m[2]) } : null;
}

function assemble(
  collected: { part: SeriesPart; sort: number }[],
  name: string,
  showIndex: boolean
): Series | null {
  if (collected.length < 2) return null;
  collected.sort((a, b) => a.sort - b.sort);

  const parts = collected.map((c) => c.part);
  const index = parts.findIndex((p) => p.current);
  return { name, parts, index, previous: parts[index - 1], next: parts[index + 1], showIndex };
}

/**
 * The series `post` belongs to, or null when it stands alone. Numbered parts
 * sort by their number rather than date, so two published the same day still
 * order correctly; the monthly analyses sort by date.
 */
export async function seriesFor(post: Post): Promise<Series | null> {
  const slug = parseId(post.id).slug;
  const entries = await getCollection('posts');

  const numbered = parseSeries(slug);
  if (numbered) {
    const collected: { part: SeriesPart; sort: number }[] = [];
    let name = numbered.key.replace(/_/g, ' ');

    for (const entry of entries) {
      const entrySlug = parseId(entry.id).slug;
      const info = parseSeries(entrySlug);
      if (info?.key !== numbered.key) continue;

      const title = entry.data.title;
      const m = title.match(SERIES_TITLE);
      if (m?.[1]) name = m[1];

      collected.push({
        sort: info.part,
        part: {
          slug: entrySlug,
          title,
          label: m?.[2]?.trim() || title,
          navLabel: `Part ${info.part}`,
          current: info.part === numbered.part,
        },
      });
    }
    const series = assemble(collected, name, true);
    if (series) series.counter = `Part ${numbered.part} of ${series.parts.length}`;
    return series;
  }

  if (ANALYSIS_SLUG.test(slug)) {
    const collected = entries
      .filter((entry) => ANALYSIS_SLUG.test(parseId(entry.id).slug))
      .map((entry) => {
        const { date, slug: entrySlug } = parseId(entry.id);
        const title = entry.data.title;
        // "January 2026 Training Analysis" reads as just "January 2026" once
        // the surrounding nav says what it is
        const label = title.match(ANALYSIS_TITLE)?.[1]?.trim() || title;
        return {
          sort: date.getTime(),
          part: { slug: entrySlug, title, label, navLabel: label, current: entrySlug === slug },
        };
      });
    return assemble(collected, 'Monthly Training Analysis', false);
  }

  return null;
}

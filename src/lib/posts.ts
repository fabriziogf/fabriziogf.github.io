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

import type { APIRoute, GetStaticPaths } from 'astro';
import { sortedPosts, parseId, formatDate } from '../../lib/posts';
import { renderCard } from '../../lib/og';

/**
 * One Open Graph card per page, rendered at build time to /og/<slug>.png.
 * Keep the slugs here in step with the pages in src/pages — a page without a
 * card falls back to the site-wide default in Base.astro.
 */

const PAGES = [
  { slug: 'site', title: 'Fabrizio GF', eyebrow: 'AI/ML product leader, builder, endurance athlete' },
  { slug: 'about', title: 'About', eyebrow: 'AI/ML product leader, builder, endurance athlete' },
  { slug: 'projects', title: 'Side Projects', eyebrow: 'Tools, models, and experiments' },
  { slug: 'training', title: 'Training Dashboard', eyebrow: 'Strava + TrainingPeaks, updated daily' },
  { slug: 'writing', title: 'Posts by Year', eyebrow: 'Writing' },
];

export const getStaticPaths: GetStaticPaths = async () => {
  const posts = (await sortedPosts()).map((post) => {
    const { date, slug } = parseId(post.id);
    return {
      params: { slug },
      props: { title: post.data.title, eyebrow: formatDate(date) },
    };
  });

  return [
    ...posts,
    ...PAGES.map(({ slug, ...props }) => ({ params: { slug }, props })),
  ];
};

export const GET: APIRoute = async ({ props }) => {
  const png = await renderCard(props as { title: string; eyebrow?: string });
  return new Response(new Uint8Array(png), {
    headers: {
      'Content-Type': 'image/png',
      'Cache-Control': 'public, max-age=31536000, immutable',
    },
  });
};

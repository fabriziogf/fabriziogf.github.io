import rss from '@astrojs/rss';
import { sortedPosts, parseId } from '../lib/posts';

export async function GET(context) {
  const posts = await sortedPosts();
  return rss({
    title: 'fabriziogf.github.io',
    description: "Fabrizio GF's personal website",
    site: context.site,
    items: posts.map((post) => {
      const { date, slug } = parseId(post.id);
      return {
        title: post.data.title,
        pubDate: date,
        link: `/${slug}/`,
      };
    }),
  });
}

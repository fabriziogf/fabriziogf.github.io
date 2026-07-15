import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// Posts stay in the original Jekyll `_posts/` directory so nothing else
// (git history, the writing workflow) has to change. Filenames follow the
// Jekyll convention: YYYY-MM-DD-Slug.md → served at /Slug/.
const posts = defineCollection({
  loader: glob({
    pattern: '*.md',
    base: './_posts',
    // Keep the exact filename (minus .md) as the id: the default generateId
    // slugifies/lowercases, which would break Jekyll-era URLs like
    // /World_Cup_prediction_model_part10/.
    generateId: ({ entry }) => entry.replace(/\.md$/, ''),
  }),
  schema: z.object({
    title: z.string(),
  }),
});

export const collections = { posts };

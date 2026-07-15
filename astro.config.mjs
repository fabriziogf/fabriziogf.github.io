import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://fabriziogf.github.io',
  trailingSlash: 'ignore',
  integrations: [sitemap()],
  markdown: {
    shikiConfig: {
      // Both themes are emitted; global.css switches them with the OS scheme.
      themes: { light: 'github-light', dark: 'github-dark' },
    },
  },
});

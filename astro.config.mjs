// Astro builds plain static pages for GitHub Pages (decided Nov 13, 2026).
// BASE_PATH comes from GitHub's configure-pages step (empty with the custom domain).
// AT_OUT lets the release-rule test build into a temporary folder.
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://awestrucktoday.org',
  base: process.env.BASE_PATH || '/',
  outDir: process.env.AT_OUT || './site',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
  devToolbar: { enabled: false },
});

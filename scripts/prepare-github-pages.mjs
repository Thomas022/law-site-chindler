import { copyFile, cp, mkdir, rm } from 'node:fs/promises';
import { join } from 'node:path';

const output = join(process.cwd(), 'dist', 'client');
const basePath = (process.env.NEXT_PUBLIC_BASE_PATH ?? '').replace(/^\//, '');
const routes = [
  'imoveis',
  'imoveis/detalhes',
  'privacidade',
  'condominio/servicos',
  'condominio/diferenciais',
  'condominio/taxa-administrativa',
];

for (const route of routes) {
  const directory = join(output, route);
  await mkdir(directory, { recursive: true });
  await copyFile(join(output, `${route}.html`), join(directory, 'index.html'));
}

// Vinext emits prefixed assets inside a matching directory. GitHub Pages already
// mounts the artifact at the repository path, so assets must live at its root.
if (basePath) {
  const prefixedAssets = join(output, basePath, '_next');
  await cp(prefixedAssets, join(output, '_next'), { recursive: true });
  await rm(join(output, basePath), { recursive: true, force: true });
}

console.log(`GitHub Pages: ${routes.length + 1} páginas preparadas.`);

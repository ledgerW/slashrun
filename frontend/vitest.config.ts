import { defineConfig } from 'vitest/config';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  test: {
    include: ['**/__tests__/**/*.{test,spec}.{ts,tsx}', '**/?(*.)+(test|spec).{ts,tsx}'],
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    css: true,
    globals: true,
    coverage: {
      reporter: ['text', 'lcov'],
      reportsDirectory: './coverage',
    },
    env: {
      NEXT_PUBLIC_API_BASE_URL: 'http://localhost:8000',
    },
  },
  esbuild: {
    jsx: 'automatic',
    jsxImportSource: 'react',
  },
  resolve: {
    alias: [
      {
        find: '@/providers',
        replacement: fileURLToPath(
          new URL('./app/(workspace)/_providers', import.meta.url),
        ),
      },
      {
        find: '@/components',
        replacement: fileURLToPath(
          new URL('./app/(workspace)/_components', import.meta.url),
        ),
      },
      { find: '@', replacement: fileURLToPath(new URL('./', import.meta.url)) },
    ],
  },
});

import { defineConfig } from 'vitest/config';
import { fileURLToPath } from 'node:url';
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: [fileURLToPath(new URL('./setup.mjs', import.meta.url))],
    include: ['src/**/*.test.{js,jsx}', 'packages/*/src/**/*.test.js', 'src/**/__tests__/*.{js,jsx}'],
    watch: false,
    maxWorkers: 1,
    testTimeout: 5000
  }
});

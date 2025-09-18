import '@testing-library/jest-dom/vitest';
import { vi } from 'vitest';

window.scrollTo = window.scrollTo || (() => undefined);

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn(),
  }),
  redirect: vi.fn(),
}));

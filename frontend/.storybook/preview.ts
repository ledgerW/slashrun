import type { Preview } from '@storybook/nextjs-vite';
import '../app/globals.css';

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    backgrounds: {
      default: 'Gotham Night',
      values: [
        { name: 'Gotham Night', value: '#05070d' },
        { name: 'Command Console', value: '#0c111c' },
      ],
    },
    a11y: {
      test: 'todo',
    },
  },
};

export default preview;

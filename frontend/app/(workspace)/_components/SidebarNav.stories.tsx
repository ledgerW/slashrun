// eslint-disable-next-line storybook/no-renderer-packages
import type { Meta, StoryObj } from '@storybook/react';
import { SidebarNav } from './SidebarNav';
import { UIStateProvider } from '../_providers/UIStateProvider';

const meta: Meta<typeof SidebarNav> = {
  title: 'Workspace/SidebarNav',
  component: SidebarNav,
  decorators: [
    (Story, context) => (
      <UIStateProvider>
        <div style={{ width: 280 }}>
          <Story {...context.args} />
        </div>
      </UIStateProvider>
    ),
  ],
};

export default meta;

type Story = StoryObj<typeof SidebarNav>;

export const Default: Story = {};

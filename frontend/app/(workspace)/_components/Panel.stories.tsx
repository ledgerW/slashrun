// eslint-disable-next-line storybook/no-renderer-packages
import type { Meta, StoryObj } from '@storybook/react';
import { Panel } from './Panel';

const meta: Meta<typeof Panel> = {
  title: 'Workspace/Panel',
  component: Panel,
  parameters: {
    layout: 'centered',
  },
  args: {
    title: 'Panel Title',
    subtitle: 'Auxiliary subtitle for context',
  },
};

export default meta;

type Story = StoryObj<typeof Panel>;

export const Default: Story = {
  args: {
    children: (
      <p style={{ maxWidth: 320 }}>
        Gotham-aligned content container used across the workspace shell for timeline,
        map, and evidence modules.
      </p>
    ),
  },
};

export const WithActions: Story = {
  args: {
    actions: <button className="label">Action</button>,
    children: (
      <ul
        style={{
          margin: 0,
          paddingLeft: '1.2rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
        }}
      >
        <li>Placeholder bullet for upcoming simulation insight.</li>
        <li>Secondary bullet to demonstrate wrapping content.</li>
      </ul>
    ),
  },
};

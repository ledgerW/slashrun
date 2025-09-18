import React from 'react';
import { render, screen } from '@testing-library/react';
import { Panel } from '@/app/(workspace)/_components/Panel';

describe('Panel', () => {
  it('renders titles and children', () => {
    render(
      <Panel title="Status" subtitle="Live">
        <p>Content inside panel</p>
      </Panel>,
    );

    expect(screen.getByRole('heading', { name: 'Status' })).toBeInTheDocument();
    expect(screen.getByText('Live')).toBeInTheDocument();
    expect(screen.getByText('Content inside panel')).toBeInTheDocument();
  });

  it('renders optional actions', () => {
    render(
      <Panel title="Status" actions={<button>Act</button>}>
        <p>Content</p>
      </Panel>,
    );

    expect(screen.getByRole('button', { name: 'Act' })).toBeInTheDocument();
  });
});

'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode, useState } from 'react';

const DEFAULT_QUERY_OPTIONS = {
  queries: {
    staleTime: 60_000,
    retry: 1,
    suspense: true,
    refetchOnWindowFocus: false,
  },
};

export function QueryProvider({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () => new QueryClient({ defaultOptions: DEFAULT_QUERY_OPTIONS }),
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

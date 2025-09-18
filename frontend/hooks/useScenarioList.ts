'use client';

import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/providers/AuthProvider';
import { scenarioListQueryOptions } from '@/lib/query/scenarios';

export function useScenarioList() {
  const { user } = useAuth();
  const userId = user?.id ?? null;

  return useQuery(scenarioListQueryOptions(userId));
}

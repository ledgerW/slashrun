import { NextResponse } from 'next/server';
import { ApiClientError } from '@/lib/api';
import { fetchScenarioDetail } from '@/lib/simulation';

interface ScenarioParams {
  params: {
    id: string;
  };
}

export async function GET(_request: Request, context: ScenarioParams) {
  const { id } = context.params;

  try {
    const scenario = await fetchScenarioDetail(id);
    return NextResponse.json({ scenario });
  } catch (error) {
    if (error instanceof ApiClientError) {
      return NextResponse.json(
        { message: error.message, status: error.status },
        { status: error.status },
      );
    }

    return NextResponse.json(
      { message: 'Failed to load scenario detail' },
      { status: 500 },
    );
  }
}

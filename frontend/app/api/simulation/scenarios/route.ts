import { NextResponse } from 'next/server';
import { ApiClientError } from '@/lib/api';
import { fetchScenarioSummaries } from '@/lib/simulation';

export async function GET() {
  try {
    const scenarios = await fetchScenarioSummaries();
    return NextResponse.json({ scenarios });
  } catch (error) {
    if (error instanceof ApiClientError) {
      return NextResponse.json(
        { message: error.message, status: error.status },
        { status: error.status },
      );
    }

    return NextResponse.json(
      { message: 'Failed to load scenarios' },
      { status: 500 },
    );
  }
}

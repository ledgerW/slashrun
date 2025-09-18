import { NextResponse } from 'next/server';
import { login } from '@/lib/auth';
import type { LoginPayload } from '@/lib/types';

export async function POST(request: Request) {
  const payload = (await request.json()) as LoginPayload;

  try {
    const user = await login(payload);
    return NextResponse.json({
      success: true,
      user: { id: user.id, email: user.email, displayName: user.displayName },
    });
  } catch (error) {
    console.error('Failed to login user', error);
    return NextResponse.json(
      {
        success: false,
        message: error instanceof Error ? error.message : 'Unable to authenticate',
      },
      { status: 401 },
    );
  }
}

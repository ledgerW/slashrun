import { NextResponse } from 'next/server';
import { apiFetch } from '@/lib/api';
import { applySessionCookie } from '@/lib/auth';
import type { AuthenticatedUser, LoginPayload } from '@/lib/types';

interface BackendLoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    name?: string;
  };
}

export async function POST(request: Request) {
  const payload = (await request.json()) as LoginPayload;

  try {
    const backendResponse = await apiFetch<BackendLoginResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
      authenticated: false,
    });

    const user: AuthenticatedUser = {
      userId: backendResponse.user.id,
      email: backendResponse.user.email,
      displayName: backendResponse.user.name,
      token: backendResponse.access_token,
    };

    const response = NextResponse.json({
      success: true,
      user: { id: user.userId, email: user.email },
    });
    applySessionCookie(response, user);
    return response;
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

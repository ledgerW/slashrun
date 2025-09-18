import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { SESSION_COOKIE_NAME } from '@/lib/constants';

const PUBLIC_PATHS = ['/login'];

function isPublicPath(pathname: string) {
  return PUBLIC_PATHS.some((path) => pathname === path || pathname.startsWith(`${path}/`));
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (pathname.startsWith('/api') || pathname.startsWith('/_next')) {
    return NextResponse.next();
  }

  const sessionToken = request.cookies.get(SESSION_COOKIE_NAME)?.value;
  const isPublic = isPublicPath(pathname);

  if (!sessionToken && !isPublic) {
    const loginUrl = new URL('/login', request.url);
    if (pathname && pathname !== '/') {
      loginUrl.searchParams.set('redirectTo', `${pathname}${request.nextUrl.search}`);
    }
    return NextResponse.redirect(loginUrl);
  }

  if (sessionToken && isPublic) {
    const workspaceUrl = new URL('/', request.url);
    return NextResponse.redirect(workspaceUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml).*)'],
};

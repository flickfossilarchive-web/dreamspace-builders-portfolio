import { NextResponse } from 'next/server';
import { ADMIN_COOKIE_NAME, createAdminSession, getAdminCredentials } from '@/lib/admin-auth';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const username = typeof body?.username === 'string' ? body.username.trim() : '';
    const password = typeof body?.password === 'string' ? body.password : '';
    const credentials = getAdminCredentials();

    if (!credentials.username || !credentials.password) {
      return NextResponse.json({ message: 'Admin credentials are not configured.' }, { status: 503 });
    }

    if (username !== credentials.username || password !== credentials.password) {
      return NextResponse.json({ message: 'Invalid username or password.' }, { status: 401 });
    }

    const response = NextResponse.json({ ok: true });
    response.cookies.set({
      name: ADMIN_COOKIE_NAME,
      value: createAdminSession(username),
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/admin',
      maxAge: 60 * 60 * 12,
    });
    return response;
  } catch {
    return NextResponse.json({ message: 'Invalid request.' }, { status: 400 });
  }
}

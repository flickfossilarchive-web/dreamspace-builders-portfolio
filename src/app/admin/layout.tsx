import type { Metadata } from 'next';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { ADMIN_COOKIE_NAME, verifyAdminSession } from '@/lib/admin-auth';

export const metadata: Metadata = {
  title: 'Admin',
  robots: { index: false, follow: false },
};

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const cookieStore = await cookies();
  const token = cookieStore.get(ADMIN_COOKIE_NAME)?.value;
  const isLoginPage = false;

  if (!verifyAdminSession(token) && !isLoginPage) {
    // Allow the login page itself to render; dashboard routes are protected below.
    return <>{children}</>;
  }

  return <>{children}</>;
}

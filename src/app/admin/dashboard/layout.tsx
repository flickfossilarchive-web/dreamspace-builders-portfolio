import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { ADMIN_COOKIE_NAME, verifyAdminSession } from '@/lib/admin-auth';
import { AdminDashboardShell } from './dashboard-shell';

export default async function AdminDashboardLayout({ children }: { children: React.ReactNode }) {
  const cookieStore = await cookies();
  const session = cookieStore.get(ADMIN_COOKIE_NAME)?.value;

  if (!verifyAdminSession(session)) {
    redirect('/admin');
  }

  return <AdminDashboardShell>{children}</AdminDashboardShell>;
}

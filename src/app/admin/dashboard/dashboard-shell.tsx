'use client';

import { useMemo, useState, type ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Home, LogOut, Mail, PlusSquare, Building2, FolderKanban } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useFirestore, useCollection } from '@/firebase';
import { collection, where, query } from 'firebase/firestore';
import type { ContactMessage } from '@/lib/types';
import { Badge } from '@/components/ui/badge';

export function AdminDashboardShell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const firestore = useFirestore();
  const unreadEnquiriesQuery = useMemo(() => {
    if (!firestore) return null;
    return query(collection(firestore, 'contact-messages'), where('read', '==', false));
  }, [firestore]);
  const { data: unreadEnquiries } = useCollection<ContactMessage>(unreadEnquiriesQuery);
  const unreadCount = unreadEnquiries?.length || 0;

  const handleLogout = async () => {
    try { await fetch('/api/admin/logout', { method: 'POST' }); } finally { router.replace('/admin'); router.refresh(); }
  };

  const adminNavLinks = [
    { href: '/admin/dashboard/enquiries', label: 'Enquiries', icon: Mail, notificationCount: unreadCount },
    { href: '/admin/dashboard/projects', label: 'Projects', icon: FolderKanban },
    { href: '/admin/dashboard/add-project', label: 'Add Project', icon: PlusSquare },
  ];

  return (
    <div className="flex min-h-screen bg-background">
      <aside className="hidden w-64 flex-shrink-0 border-r bg-secondary/30 p-4 md:flex md:flex-col">
        <div className="mb-10 flex items-center gap-2 p-2"><Building2 className="h-8 w-8 text-primary" /><span className="font-headline text-xl font-bold">Admin</span></div>
        <nav className="flex flex-1 flex-col gap-2" aria-label="Admin navigation">
          {adminNavLinks.map((link) => <Link key={link.href} href={link.href} className={cn('flex items-center justify-between gap-3 rounded-xl px-3 py-2.5 text-sm text-muted-foreground transition hover:bg-primary/10 hover:text-primary', pathname === link.href && 'bg-primary/10 font-semibold text-primary')}><span className="flex items-center gap-3"><link.icon className="h-5 w-5" />{link.label}</span>{link.notificationCount && link.notificationCount > 0 ? <Badge className="h-6 min-w-6 rounded-full bg-primary text-primary-foreground">{link.notificationCount}</Badge> : null}</Link>)}
        </nav>
        <div className="space-y-2"><Link href="/" className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-muted-foreground hover:bg-primary/10 hover:text-primary"><Home className="h-5 w-5" />Back to Site</Link><Button variant="ghost" onClick={handleLogout} className="w-full justify-start gap-3 rounded-xl px-3 text-muted-foreground hover:bg-primary/10 hover:text-primary"><LogOut className="h-5 w-5" />Logout</Button></div>
      </aside>
      <div className="flex-1 p-4 sm:p-6 lg:p-8">{children}</div>
    </div>
  );
}

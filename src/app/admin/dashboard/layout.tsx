'use client';
import { useEffect, type ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Home, LogOut, Mail, PlusSquare, Building2 } from 'lucide-react';
import { cn } from '@/lib/utils';


const adminNavLinks = [
    { href: '/admin/dashboard/enquiries', label: 'Enquiries', icon: Mail },
    { href: '/admin/dashboard/add-project', label: 'Add Project', icon: PlusSquare },
]

export default function AdminDashboardLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    try {
        const isAuthenticated = sessionStorage.getItem('admin-authenticated') === 'true';
        if (!isAuthenticated) {
            router.replace('/admin');
        }
    } catch (e) {
        console.error("Could not access session storage. Redirecting to login.");
        router.replace('/admin');
    }
  }, [router]);

  const handleLogout = () => {
    try {
        sessionStorage.removeItem('admin-authenticated');
    } catch(e) {
        console.error("Could not access session storage.");
    }
    router.replace('/admin');
  };

  return (
    <div className="flex min-h-screen">
        <aside className="w-64 flex-shrink-0 bg-secondary/60 border-r p-4 flex flex-col">
            <div className="flex items-center space-x-2 mb-10 p-2">
                <Building2 className="h-8 w-8 text-primary" />
                <span className="text-xl font-bold font-headline">Admin</span>
            </div>
            <nav className="flex flex-col space-y-2 flex-grow">
                {adminNavLinks.map(link => (
                    <Link 
                        key={link.href}
                        href={link.href} 
                        className={cn(
                            "flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary hover:bg-primary/10",
                            pathname === link.href && "bg-primary/10 text-primary font-semibold"
                        )}>
                        <link.icon className="h-5 w-5" />
                        {link.label}
                    </Link>
                ))}
            </nav>
            <div className="mt-auto space-y-2">
                 <Link 
                    href="/" 
                    className="flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary hover:bg-primary/10"
                    >
                    <Home className="h-5 w-5" />
                    Back to Site
                </Link>
                <Button variant="ghost" onClick={handleLogout} className="w-full justify-start gap-3 px-3 text-muted-foreground hover:text-primary">
                    <LogOut className="h-5 w-5" />
                    Logout
                </Button>
            </div>
        </aside>
        <div className="flex-1 p-8 bg-background">
            {children}
        </div>
    </div>
  );
}

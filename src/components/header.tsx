'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { Building2, Menu, ArrowRight, Phone } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import { cn } from '@/lib/utils';

const navLinks = [
  { href: '/', label: 'Home' },
  { href: '/about', label: 'About' },
  { href: '/projects', label: 'Projects' },
  { href: '/contact', label: 'Contact' },
];

export function Header() {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-[#0d1724]/95 text-white shadow-lg backdrop-blur-md supports-[backdrop-filter]:bg-[#0d1724]/80">
      <div className="section-shell flex h-[76px] items-center">
        <Link href="/" className="group flex items-center gap-3" aria-label="Dreamspace Builders home">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl border border-primary/35 bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-[#0d1724]">
            <Building2 className="h-5 w-5" />
          </span>
          <span className="leading-none">
            <span className="block text-base font-bold tracking-wide sm:text-lg">DREAMSPACE</span>
            <span className="mt-1 block text-[10px] font-semibold uppercase tracking-[0.28em] text-primary">Builders</span>
          </span>
        </Link>

        <nav className="ml-auto hidden items-center gap-8 md:flex" aria-label="Main navigation">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                'relative py-2 text-sm font-semibold transition-colors hover:text-primary',
                pathname === link.href ? 'text-primary' : 'text-white/72'
              )}
            >
              {link.label}
              {pathname === link.href && <span className="absolute inset-x-0 -bottom-[17px] h-0.5 bg-primary" />}
            </Link>
          ))}
        </nav>

        <div className="ml-7 hidden items-center gap-4 lg:flex">
          <a href="tel:+919008592532" className="inline-flex items-center gap-2 text-sm font-semibold text-white/80 transition-colors hover:text-primary">
            <Phone className="h-4 w-4 text-primary" /> +91 9008592532
          </a>
          <Button asChild className="rounded-xl bg-primary font-bold text-[#0d1724] hover:bg-primary/90">
            <Link href="/contact">Get a quote <ArrowRight className="ml-2 h-4 w-4" /></Link>
          </Button>
        </div>

        <div className="ml-auto md:hidden">
          <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="text-white hover:bg-white/10 hover:text-white" aria-label="Open menu">
                <Menu className="h-6 w-6" />
                <span className="sr-only">Open menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-[86vw] border-white/10 bg-[#0d1724] text-white">
              <SheetTitle className="sr-only">Mobile Menu</SheetTitle>
              <div className="pt-8">
                <div className="mb-8 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary"><Building2 className="h-5 w-5" /></div>
                  <span className="text-lg font-bold tracking-wide">DREAMSPACE</span>
                </div>
                <nav className="flex flex-col gap-6" aria-label="Mobile navigation">
                  {navLinks.map((link) => (
                    <Link
                      key={link.href}
                      href={link.href}
                      onClick={() => setIsMobileMenuOpen(false)}
                      className={cn('text-lg font-semibold', pathname === link.href ? 'text-primary' : 'text-white/75')}
                    >
                      {link.label}
                    </Link>
                  ))}
                </nav>
                <div className="mt-10 space-y-4 border-t border-white/10 pt-7">
                  <a href="tel:+919008592532" className="flex items-center gap-3 text-sm font-semibold text-white/80"><Phone className="h-4 w-4 text-primary" /> +91 9008592532</a>
                  <Button asChild className="w-full rounded-xl bg-primary font-bold text-[#0d1724] hover:bg-primary/90">
                    <Link href="/contact" onClick={() => setIsMobileMenuOpen(false)}>Get a quote <ArrowRight className="ml-2 h-4 w-4" /></Link>
                  </Button>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}

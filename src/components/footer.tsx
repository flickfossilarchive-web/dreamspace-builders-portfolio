import Link from 'next/link';
import { Building2, Mail, MapPin, Phone } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t border-border/40 bg-background">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
          <div>
            <div className="flex items-center gap-3">
              <Building2 className="h-7 w-7 text-primary" />
              <div>
                <p className="font-bold text-lg font-headline">Dreamspace Builders</p>
                <p className="text-xs text-muted-foreground">BUILT By YOU.....</p>
              </div>
            </div>
            <p className="mt-5 text-sm leading-6 text-muted-foreground max-w-sm">
              Construction and design services for residential, commercial and industrial projects in Davanagere, Karnataka.
            </p>
          </div>
          <div>
            <p className="font-semibold font-headline mb-4">Contact</p>
            <div className="space-y-3 text-sm text-muted-foreground">
              <a href="tel:+919008592532" className="flex items-start gap-3 hover:text-primary transition-colors"><Phone className="h-4 w-4 mt-0.5 shrink-0" /><span>+91 9008592532</span></a>
              <a href="mailto:Dreamspacebuilders12@gmail.com" className="flex items-start gap-3 hover:text-primary transition-colors"><Mail className="h-4 w-4 mt-0.5 shrink-0" /><span>Dreamspacebuilders12@gmail.com</span></a>
              <a href="https://www.google.com/maps/search/?api=1&query=%2370%2F7%2C%2015th%20Cross%20Road%2C%20Nijalingappa%20Layout%2C%20Davanagere%20577004" target="_blank" rel="noreferrer" className="flex items-start gap-3 hover:text-primary transition-colors"><MapPin className="h-4 w-4 mt-0.5 shrink-0" /><span>#70/7, 15th Cross Road, Nijalingappa Layout, Davanagere - 577004</span></a>
            </div>
          </div>
          <div>
            <p className="font-semibold font-headline mb-4">Explore</p>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <Link href="/" className="text-muted-foreground hover:text-primary transition-colors">Home</Link>
              <Link href="/about" className="text-muted-foreground hover:text-primary transition-colors">About</Link>
              <Link href="/projects" className="text-muted-foreground hover:text-primary transition-colors">Projects</Link>
              <Link href="/contact" className="text-muted-foreground hover:text-primary transition-colors">Contact</Link>
            </div>
            <p className="mt-6 text-xs text-muted-foreground">GSTIN: 29DFEPP1670H1Z7</p>
          </div>
        </div>
        <div className="mt-10 pt-6 border-t border-border/40 flex flex-col sm:flex-row justify-between gap-3 text-xs text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} Dreamspace Builders. All rights reserved.</p>
          <p>Built for clear communication, strong execution, and lasting spaces.</p>
        </div>
      </div>
    </footer>
  );
}

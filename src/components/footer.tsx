import Link from 'next/link';
import { Building2 } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t border-border/40 bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center text-center md:text-left gap-6">
          <div className="flex items-center">
            <Building2 className="h-7 w-7 mr-3 text-primary" />
            <div >
                <p className="font-bold text-lg font-headline">Dreamspace Builders</p>
                <p className="text-xs text-muted-foreground">BUILT By YOU.....</p>
            </div>
          </div>
          <div className="text-sm text-muted-foreground">
            <p>&copy; {new Date().getFullYear()} Dreamspace Builders. All rights reserved.</p>
             <p className="text-xs mt-1">GSTIN: 29DFEPP1670H1Z7</p>
          </div>
          <div className="flex space-x-4">
            <Link href="/projects" className="text-sm text-muted-foreground hover:text-primary transition-colors">Projects</Link>
            <Link href="/about" className="text-sm text-muted-foreground hover:text-primary transition-colors">About</Link>
            <Link href="/contact" className="text-sm text-muted-foreground hover:text-primary transition-colors">Contact</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}

import Link from 'next/link';
import { Building2 } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t bg-secondary">
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center mb-4 md:mb-0">
            <Building2 className="h-6 w-6 mr-2 text-primary" />
            <span className="font-bold text-lg font-headline">DreamSpace Builders</span>
          </div>
          <div className="text-center md:text-left mb-4 md:mb-0">
            <p className="text-sm text-muted-foreground">&copy; {new Date().getFullYear()} DreamSpace Builders. All rights reserved.</p>
            <p className="text-xs text-muted-foreground mt-1">Building the Future, One Project at a Time.</p>
          </div>
          <div className="flex space-x-4">
          </div>
        </div>
      </div>
    </footer>
  );
}

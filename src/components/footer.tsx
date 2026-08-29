import Link from 'next/link';
import { ArrowRight, Building2, Mail, MapPin, Phone } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t border-white/10 bg-[#08121f] text-white">
      <div className="section-shell py-14 md:py-16">
        <div className="grid gap-12 lg:grid-cols-[1.25fr_0.8fr_0.8fr]">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary"><Building2 className="h-5 w-5" /></div>
              <div>
                <p className="text-lg font-bold tracking-wide">DREAMSPACE</p>
                <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-primary">Builders</p>
              </div>
            </div>
            <p className="mt-6 max-w-md text-sm leading-7 text-white/55">Construction and design services for residential, commercial and industrial projects in Davanagere, Karnataka.</p>
            <Link href="/contact" className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-primary hover:text-white">Start a project <ArrowRight className="h-4 w-4" /></Link>
          </div>

          <div>
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-white/90">Contact</p>
            <div className="mt-5 space-y-4 text-sm text-white/60">
              <a href="tel:+919008592532" className="flex items-start gap-3 hover:text-primary"><Phone className="mt-0.5 h-4 w-4 shrink-0 text-primary" /><span>+91 9008592532</span></a>
              <a href="mailto:Dreamspacebuilders12@gmail.com" className="flex items-start gap-3 hover:text-primary"><Mail className="mt-0.5 h-4 w-4 shrink-0 text-primary" /><span className="break-all">Dreamspacebuilders12@gmail.com</span></a>
              <a href="https://www.google.com/maps/search/?api=1&query=%2370%2F7%2C%2015th%20Cross%20Road%2C%20Nijalingappa%20Layout%2C%20Davanagere%20577004" target="_blank" rel="noreferrer" className="flex items-start gap-3 hover:text-primary"><MapPin className="mt-0.5 h-4 w-4 shrink-0 text-primary" /><span>#70/7, 15th Cross Road, Nijalingappa Layout, Davanagere - 577004</span></a>
            </div>
          </div>

          <div>
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-white/90">Explore</p>
            <div className="mt-5 grid grid-cols-2 gap-4 text-sm text-white/60">
              <Link href="/" className="hover:text-primary">Home</Link>
              <Link href="/about" className="hover:text-primary">About</Link>
              <Link href="/projects" className="hover:text-primary">Projects</Link>
              <Link href="/contact" className="hover:text-primary">Contact</Link>
            </div>
            <p className="mt-7 text-xs text-white/35">GSTIN: 29DFEPP1670H1Z7</p>
          </div>
        </div>

        <div className="mt-12 flex flex-col gap-3 border-t border-white/10 pt-6 text-xs text-white/35 sm:flex-row sm:items-center sm:justify-between">
          <p>&copy; {new Date().getFullYear()} Dreamspace Builders. All rights reserved.</p>
          <p>Built around clear communication and dependable execution.</p>
        </div>
      </div>
    </footer>
  );
}

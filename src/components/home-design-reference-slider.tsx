'use client';

import { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, ArrowRight, Images } from 'lucide-react';
import { Button } from '@/components/ui/button';

const slides = [
  { src: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1800&q=88', title: 'Modern Minimalist', copy: 'Clean geometry, open glazing and calm material palettes.', alt: 'Modern minimalist residential facade with clean geometric lines' },
  { src: 'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1800&q=88', title: 'Contemporary Elegance', copy: 'Layered volumes, warm timber and refined exterior lighting.', alt: 'Contemporary luxury home exterior with warm architectural lighting' },
  { src: 'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1800&q=88', title: 'Urban Sophistication', copy: 'Vertical proportions and strong facade composition for city homes.', alt: 'Sophisticated urban residence with modern facade composition' },
  { src: 'https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&w=1800&q=88', title: 'Luxury Living', copy: 'Premium finishes, generous glazing and statement entry details.', alt: 'Luxury modern residence with premium finishes and glazing' },
  { src: 'https://images.unsplash.com/photo-1600573472550-8090b5e5b9e3?auto=format&fit=crop&w=1800&q=88', title: 'Warm Modern', copy: 'Natural textures and greenery paired with contemporary forms.', alt: 'Warm modern home with natural materials and landscaping' },
  { src: 'https://images.unsplash.com/photo-1600585154363-67eb9e2e2099?auto=format&fit=crop&w=1800&q=88', title: 'Architectural Statement', copy: 'Distinctive massing and crisp detailing designed to stand out.', alt: 'Modern architectural residence with distinctive massing' },
];

export function HomeDesignReferenceSlider() {
  const pathname = usePathname();
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (pathname !== '/') return;
    const timer = window.setInterval(() => setIndex((current) => (current + 1) % slides.length), 5500);
    return () => window.clearInterval(timer);
  }, [pathname]);

  if (pathname !== '/') return null;
  const slide = slides[index];
  const go = (next: number) => setIndex((next + slides.length) % slides.length);

  return (
    <section className="bg-secondary py-24 md:py-28">
      <div className="section-shell">
        <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
          <div className="max-w-3xl">
            <p className="eyebrow">House design inspiration</p>
            <h2 className="display-title mt-4 text-4xl sm:text-5xl">{slide.title}. Explore the look you love.</h2>
            <p className="mt-5 max-w-2xl text-base leading-8 text-muted-foreground">{slide.copy} Browse more contemporary facade ideas before we shape a practical, buildable direction around your requirements.</p>
          </div>
          <Button asChild variant="outline" className="rounded-xl"><Link href="/design-reference">View all references <ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
        </div>

        <div className="mt-12 overflow-hidden rounded-3xl border bg-[#0d1724] shadow-xl">
          <div className="grid lg:grid-cols-[0.58fr_1.42fr]">
            <div className="flex flex-col justify-between p-7 text-white sm:p-10 md:p-12">
              <div>
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary"><Images className="h-6 w-6" /></div>
                <p className="mt-7 text-sm font-semibold uppercase tracking-[0.18em] text-primary">Reference {String(index + 1).padStart(2, '0')} / {String(slides.length).padStart(2, '0')}</p>
                <h3 className="mt-4 text-2xl font-semibold sm:text-3xl">{slide.title}</h3>
                <p className="mt-3 max-w-md text-sm leading-7 text-white/62 sm:text-base">Concept inspiration only — completed Dreamspace projects are shown separately in the portfolio.</p>
              </div>
              <div className="mt-10 flex items-center gap-3">
                <button type="button" onClick={() => go(index - 1)} className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/15 text-white transition hover:border-primary hover:text-primary" aria-label="Previous design reference"><ArrowLeft className="h-5 w-5" /></button>
                <button type="button" onClick={() => go(index + 1)} className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/15 text-white transition hover:border-primary hover:text-primary" aria-label="Next design reference"><ArrowRight className="h-5 w-5" /></button>
                <div className="ml-2 flex gap-2" aria-label="Design reference slides">
                  {slides.map((item, dot) => <button type="button" key={item.src} onClick={() => setIndex(dot)} aria-label={`Show design reference ${dot + 1}`} className={`h-2.5 rounded-full transition-all ${dot === index ? 'w-8 bg-primary' : 'w-2.5 bg-white/25'}`} />)}
                </div>
              </div>
            </div>
            <div className="min-h-[380px] bg-white/5 p-3 sm:p-5 md:min-h-[480px]">
              <div className="h-full overflow-hidden rounded-2xl border border-white/10 bg-white">
                <img src={slide.src} alt={slide.alt} loading={index === 0 ? 'eager' : 'lazy'} decoding="async" className="h-full min-h-[380px] w-full object-cover md:min-h-[480px]" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

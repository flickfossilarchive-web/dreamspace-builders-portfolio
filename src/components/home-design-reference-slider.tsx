'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, ArrowRight, Images } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ReferenceImage } from '@/components/reference-image';

const slides = [
  { src: '/house-designs/residential-design-gallery.webp', eyebrow: 'House design inspiration', title: 'Start with the look you love.', copy: 'Explore facade ideas, materials, proportions and architectural details before we turn your preferences into a project brief.', count: '9 design references' },
  { src: '/house-designs/residential-design-gallery-more.b64', eyebrow: 'More design directions', title: 'Compare styles before you build.', copy: 'See more residential references covering different massing, balcony treatments, colours, lighting and exterior detailing.', count: '4 design references' },
];

export function HomeDesignReferenceSlider() {
  const [index, setIndex] = useState(0);
  const slide = slides[index];
  useEffect(() => {
    const timer = window.setInterval(() => setIndex((current) => (current + 1) % slides.length), 6500);
    return () => window.clearInterval(timer);
  }, []);
  const go = (next: number) => setIndex((next + slides.length) % slides.length);

  return (
    <section className="bg-secondary py-24 md:py-28">
      <div className="section-shell">
        <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
          <div className="max-w-3xl">
            <p className="eyebrow">{slide.eyebrow}</p>
            <h2 className="display-title mt-4 text-4xl sm:text-5xl">{slide.title}</h2>
            <p className="mt-5 max-w-2xl text-base leading-8 text-muted-foreground">{slide.copy}</p>
          </div>
          <Button asChild variant="outline" className="rounded-xl"><Link href="/design-reference">View all references <ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
        </div>

        <div className="mt-12 overflow-hidden rounded-3xl border bg-[#0d1724] shadow-xl">
          <div className="grid lg:grid-cols-[0.82fr_1.18fr]">
            <div className="flex flex-col justify-between p-7 text-white sm:p-10 md:p-12">
              <div>
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary"><Images className="h-6 w-6" /></div>
                <p className="mt-7 text-sm font-semibold uppercase tracking-[0.18em] text-white/45">{slide.count}</p>
                <p className="mt-3 max-w-md text-sm leading-7 text-white/62 sm:text-base">Reference concepts only — actual completed projects are published separately by the Dreamspace team.</p>
              </div>
              <div className="mt-10 flex items-center gap-3">
                <button type="button" onClick={() => go(index - 1)} className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/15 text-white transition hover:border-primary hover:text-primary" aria-label="Previous reference set"><ArrowLeft className="h-5 w-5" /></button>
                <button type="button" onClick={() => go(index + 1)} className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/15 text-white transition hover:border-primary hover:text-primary" aria-label="Next reference set"><ArrowRight className="h-5 w-5" /></button>
                <div className="ml-2 flex gap-2" aria-label="Reference slides">
                  {slides.map((item, dot) => <button type="button" key={item.src} onClick={() => setIndex(dot)} aria-label={`Show reference set ${dot + 1}`} className={`h-2.5 rounded-full transition-all ${dot === index ? 'w-8 bg-primary' : 'w-2.5 bg-white/25'}`} />)}
                </div>
              </div>
            </div>
            <div className="min-h-[360px] bg-white/5 p-3 sm:p-5 md:min-h-[440px]">
              <div className="h-full overflow-hidden rounded-2xl border border-white/10 bg-white">
                <ReferenceImage src={slide.src} alt="Residential architectural design reference collage" className="h-full min-h-[360px] w-full object-contain md:min-h-[440px]" priority={index === 0} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { ArrowLeft, ArrowRight, House, Leaf, Ruler, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

const references = [
  { src: '/generated/design-references/reference-01.svg', title: 'Contemporary Elegance', copy: 'Balanced volumes, warm materials and a refined street presence.' },
  { src: '/generated/design-references/reference-02.svg', title: 'Modern Minimalist', copy: 'Clean lines, generous glazing and calm architectural proportions.' },
  { src: '/generated/design-references/reference-03.svg', title: 'Architectural Harmony', copy: 'Strong geometry, layered textures and carefully framed openings.' },
  { src: '/generated/design-references/reference-04.svg', title: 'Futuristic Design', copy: 'Expressive curves, dramatic forms and statement architecture.' },
  { src: '/generated/design-references/reference-05.svg', title: 'Luxury Living', copy: 'Premium facade detailing with greenery, light and privacy in mind.' },
  { src: '/generated/design-references/reference-06.svg', title: 'Urban Sophistication', copy: 'A bold city-home direction that makes efficient use of space.' },
];

export function HomeDesignShowcase() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => setIndex((current) => (current + 1) % references.length), 6500);
    return () => window.clearInterval(timer);
  }, []);

  const slide = references[index];
  const heroPanels = [
    references[index],
    references[(index + 1) % references.length],
    references[(index + 2) % references.length],
    references[(index + 3) % references.length],
  ];

  const go = (next: number) => setIndex((next + references.length) % references.length);

  return (
    <>
      <section className="relative overflow-hidden bg-[#08121f] text-white">
        <div className="grid min-h-[520px] grid-cols-1 md:grid-cols-4">
          {heroPanels.map((panel, panelIndex) => (
            <div key={`${panel.src}-${panelIndex}`} className="relative min-h-[340px] overflow-hidden border-b border-white/10 md:min-h-[520px] md:border-b-0 md:border-r last:md:border-r-0">
              <img src={panel.src} alt={panel.title} className="h-full min-h-[340px] w-full object-cover md:min-h-[520px]" />
              <div className="absolute inset-0 bg-gradient-to-t from-[#08121f]/85 via-transparent to-[#08121f]/10" />
              {panelIndex === 0 && (
                <div className="absolute inset-0 flex items-end p-7 sm:p-10 lg:p-12">
                  <div className="max-w-md">
                    <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] backdrop-blur-sm">
                      <Sparkles className="h-4 w-4 text-primary" /> Design inspiration
                    </div>
                    <h1 className="display-title text-4xl leading-[1.02] text-white sm:text-5xl lg:text-6xl">Designing Spaces.<span className="block text-white/85">Building Dreams.</span></h1>
                    <p className="mt-5 max-w-sm text-sm leading-7 text-white/70 sm:text-base">Original architectural concepts to help you find the facade, mood and details that fit your home.</p>
                    <Button asChild className="mt-7 rounded-xl bg-primary font-bold text-[#08121f] hover:bg-primary/90">
                      <Link href="/design-reference">View design references <ArrowRight className="ml-2 h-4 w-4" /></Link>
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <button type="button" onClick={() => go(index - 1)} aria-label="Previous design inspiration" className="absolute left-4 top-1/2 z-10 -translate-y-1/2 inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/25 bg-black/30 text-white backdrop-blur-sm transition hover:border-primary hover:text-primary sm:left-7">
          <ArrowLeft className="h-5 w-5" />
        </button>
        <button type="button" onClick={() => go(index + 1)} aria-label="Next design inspiration" className="absolute right-4 top-1/2 z-10 -translate-y-1/2 inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/25 bg-black/30 text-white backdrop-blur-sm transition hover:border-primary hover:text-primary sm:right-7">
          <ArrowRight className="h-5 w-5" />
        </button>
        <div className="absolute bottom-5 left-1/2 z-10 flex -translate-x-1/2 gap-2 rounded-full border border-white/10 bg-black/20 px-3 py-2 backdrop-blur-sm">
          {references.map((item, dot) => (
            <button key={item.src} type="button" onClick={() => setIndex(dot)} aria-label={`Show ${item.title}`} className={`h-2.5 rounded-full transition-all ${dot === index ? 'w-8 bg-primary' : 'w-2.5 bg-white/60'}`} />
          ))}
        </div>
      </section>

      <section className="bg-background py-20 md:py-24">
        <div className="section-shell">
          <div className="grid gap-10 lg:grid-cols-[0.95fr_1.05fr] lg:items-start lg:gap-16">
            <div>
              <p className="eyebrow">Design inspiration</p>
              <h2 className="display-title mt-4 text-4xl sm:text-5xl">House design ideas to inspire you.</h2>
              <p className="mt-5 max-w-xl text-base leading-8 text-muted-foreground">Explore a curated collection of original residential concepts. Use them to communicate the look you like before we shape a practical brief around your site, budget and lifestyle.</p>
              <Button asChild className="mt-7 rounded-xl bg-[#08121f] font-semibold text-white hover:bg-[#122236]"><Link href="/design-reference">View all references <ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
            </div>

            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
              {[['Modern facades', 'Contemporary & elegant styles', House], ['Smart spaces', 'Thoughtful layouts for living', Ruler], ['Premium materials', 'Details built to last', Leaf], ['Creative concepts', 'Ideas tailored to you', Sparkles]].map(([title, copy, Icon]) => (
                <div key={String(title)} className="border-l border-border pl-5 first:border-l-0 first:pl-0 sm:first:border-l sm:first:pl-5">
                  <Icon className="h-6 w-6 text-primary" />
                  <h3 className="mt-4 text-sm font-bold">{title}</h3>
                  <p className="mt-2 text-xs leading-5 text-muted-foreground">{copy}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {references.map((reference) => (
              <Link key={reference.src} href="/design-reference" className="group relative overflow-hidden rounded-2xl border bg-[#08121f] shadow-sm transition hover:-translate-y-1 hover:shadow-xl">
                <div className="aspect-[4/3] overflow-hidden">
                  <img src={reference.src} alt={reference.title} loading="lazy" className="h-full w-full object-cover transition duration-500 group-hover:scale-[1.03]" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-transparent to-transparent" />
                </div>
                <div className="absolute inset-x-0 bottom-0 p-5 text-white">
                  <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-primary">Reference concept</p>
                  <h3 className="mt-2 text-lg font-semibold">{reference.title}</h3>
                  <p className="mt-1 text-sm text-white/70">{reference.copy}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}

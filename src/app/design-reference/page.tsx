import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ReferenceImage } from '@/components/reference-image';

export const metadata = {
  title: 'Design References | Dreamspace Builders',
  description: 'Browse residential design references shared for inspiration by Dreamspace Builders. These visuals are concepts and references, not completed project records.',
  alternates: { canonical: 'https://www.dreamspacebuilders12.com/design-reference' },
  openGraph: {
    title: 'Design References | Dreamspace Builders',
    description: 'Residential facade and architectural design references for inspiration.',
    url: 'https://www.dreamspacebuilders12.com/design-reference',
    type: 'website',
  },
};

export default function DesignReferencePage() {
  return (
    <div className="bg-background">
      <section className="bg-[#0d1724] py-20 text-white md:py-28">
        <div className="section-shell">
          <p className="eyebrow text-primary">Design references</p>
          <h1 className="display-title mt-4 max-w-4xl text-5xl text-white sm:text-6xl md:text-7xl">Ideas to help shape your home.</h1>
          <p className="mt-6 max-w-2xl text-base leading-8 text-white/65 sm:text-lg">Browse residential design references shared for inspiration. These visuals help start conversations about facade styles, proportions, materials and overall direction; they are not presented as completed Dreamspace projects.</p>
        </div>
      </section>

      <section className="section-shell py-16 md:py-24">
        <div className="grid gap-8 lg:grid-cols-2">
          <article className="overflow-hidden rounded-3xl border bg-card shadow-sm">
            <div className="bg-[#0d1724] p-3 sm:p-5"><div className="min-h-[420px] overflow-hidden rounded-2xl bg-white"><ReferenceImage src="/house-designs/residential-design-gallery.webp" alt="Residential architectural facade design references and house design concepts" className="h-full min-h-[420px] w-full object-contain" priority /></div></div>
            <div className="p-6 md:p-8"><p className="eyebrow text-primary">Reference set A</p><h2 className="mt-3 text-2xl font-semibold tracking-[-0.015em] md:text-3xl">Contemporary facade directions</h2><p className="mt-3 text-sm leading-7 text-muted-foreground md:text-base">A visual mix of modern residential elevations, materials, landscaping and lighting ideas to help define a preferred direction.</p></div>
          </article>

          <article className="overflow-hidden rounded-3xl border bg-card shadow-sm">
            <div className="bg-[#0d1724] p-3 sm:p-5"><div className="min-h-[420px] overflow-hidden rounded-2xl bg-white"><ReferenceImage src="/house-designs/residential-design-gallery-more.b64" alt="Additional residential architectural design references and facade concepts" className="h-full min-h-[420px] w-full object-contain" /></div></div>
            <div className="p-6 md:p-8"><p className="eyebrow text-primary">Reference set B</p><h2 className="mt-3 text-2xl font-semibold tracking-[-0.015em] md:text-3xl">More residential ideas</h2><p className="mt-3 text-sm leading-7 text-muted-foreground md:text-base">Additional facade concepts covering different forms, colour palettes, balcony treatments and exterior detailing.</p></div>
          </article>
        </div>

        <div className="mt-14 rounded-3xl bg-[#0d1724] p-7 text-white sm:p-10 md:mt-20"><div className="flex flex-col gap-7 lg:flex-row lg:items-center lg:justify-between"><div><p className="eyebrow text-primary">Ready to make it yours?</p><h2 className="mt-3 max-w-2xl text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">Share a reference. We’ll help shape the brief.</h2><p className="mt-3 max-w-2xl text-sm leading-7 text-white/65 sm:text-base">Tell us what you like about a reference image and we can discuss the right direction for your site, budget and requirements.</p></div><Button asChild className="shrink-0 rounded-xl bg-primary font-bold text-[#0d1724] hover:bg-primary/90"><Link href="/contact">Discuss your design <ArrowRight className="ml-2 h-4 w-4" /></Link></Button></div></div>
      </section>
    </div>
  );
}

import Link from 'next/link';
import { ArrowRight, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';

const references = [
  { src: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1800&q=88', title: 'Modern Minimalist', copy: 'Clean geometry, open glazing and calm material palettes.', alt: 'Modern minimalist residential facade with clean geometric lines' },
  { src: 'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1800&q=88', title: 'Contemporary Elegance', copy: 'Layered volumes, warm timber and refined exterior lighting.', alt: 'Contemporary luxury home exterior with warm architectural lighting' },
  { src: 'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1800&q=88', title: 'Urban Sophistication', copy: 'Vertical proportions and strong facade composition for city homes.', alt: 'Sophisticated urban residence with modern facade composition' },
  { src: 'https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&w=1800&q=88', title: 'Luxury Living', copy: 'Premium finishes, generous glazing and statement entry details.', alt: 'Luxury modern residence with premium finishes and glazing' },
  { src: 'https://images.unsplash.com/photo-1600573472550-8090b5e5b9e3?auto=format&fit=crop&w=1800&q=88', title: 'Warm Modern', copy: 'Natural textures and greenery paired with contemporary forms.', alt: 'Warm modern home with natural materials and landscaping' },
  { src: 'https://images.unsplash.com/photo-1600585154363-67eb9e2e2099?auto=format&fit=crop&w=1800&q=88', title: 'Architectural Statement', copy: 'Distinctive massing and crisp detailing designed to stand out.', alt: 'Modern architectural residence with distinctive massing' },
];

export const metadata = {
  title: 'Design References | Dreamspace Builders',
  description: 'High-quality residential facade and architectural design references for inspiration by Dreamspace Builders. These are inspiration visuals, not completed project records.',
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
          <h1 className="display-title mt-4 max-w-4xl text-5xl text-white sm:text-6xl md:text-7xl">Ideas to shape your next home.</h1>
          <p className="mt-6 max-w-3xl text-base leading-8 text-white/65 sm:text-lg">A curated visual library of contemporary residential facades, proportions, materials, landscaping and lighting ideas. These references are inspiration visuals and are not presented as completed Dreamspace projects.</p>
        </div>
      </section>

      <section className="section-shell py-16 md:py-24">
        <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="eyebrow">Curated inspiration</p>
            <h2 className="display-title mt-4 text-4xl sm:text-5xl">Modern designs. Different directions.</h2>
            <p className="mt-5 max-w-2xl text-base leading-8 text-muted-foreground">Use these references to identify the mood, facade language and details you like before we shape a buildable brief around your site and requirements.</p>
          </div>
          <Button asChild variant="outline" className="rounded-xl"><Link href="/contact">Discuss your design <ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
        </div>

        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {references.map((reference) => (
            <article key={reference.src} className="group overflow-hidden rounded-3xl border bg-card shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
              <a href={reference.src} target="_blank" rel="noreferrer" className="block" aria-label={`Open ${reference.title} reference image`}>
                <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
                  <img src={reference.src} alt={reference.alt} loading="lazy" decoding="async" className="h-full w-full object-cover transition duration-500 group-hover:scale-[1.03]" />
                  <span className="absolute right-4 top-4 inline-flex h-10 w-10 items-center justify-center rounded-full border border-white/40 bg-black/35 text-white backdrop-blur-sm"><ExternalLink className="h-4 w-4" /></span>
                </div>
              </a>
              <div className="p-6 md:p-7">
                <p className="eyebrow text-primary">Reference concept</p>
                <h3 className="mt-3 text-2xl font-semibold tracking-[-0.015em]">{reference.title}</h3>
                <p className="mt-3 text-sm leading-7 text-muted-foreground">{reference.copy}</p>
              </div>
            </article>
          ))}
        </div>

        <div className="mt-16 overflow-hidden rounded-3xl bg-[#0d1724] text-white md:mt-20">
          <div className="grid lg:grid-cols-[0.8fr_1.2fr]">
            <div className="p-7 sm:p-10 md:p-12">
              <p className="eyebrow text-primary">Ready to make it yours?</p>
              <h2 className="mt-3 max-w-2xl text-3xl font-semibold tracking-[-0.02em] sm:text-4xl">Bring us the reference. We’ll build the brief.</h2>
              <p className="mt-4 max-w-2xl text-sm leading-7 text-white/65 sm:text-base">Tell us which styles you prefer, what you want to change, and the kind of home you are planning. We can then discuss a practical direction for your site, budget and execution.</p>
              <Button asChild className="mt-7 rounded-xl bg-primary font-bold text-[#0d1724] hover:bg-primary/90"><Link href="/contact">Start a conversation <ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
            </div>
            <div className="grid grid-cols-2 gap-3 bg-white/[0.04] p-3 sm:p-5">
              {references.slice(0, 4).map((reference) => <img key={reference.src} src={reference.src} alt="Residential design reference" loading="lazy" decoding="async" className="h-full min-h-44 w-full rounded-2xl object-cover" />)}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, ArrowRight, Images } from 'lucide-react';
import { Button } from '@/components/ui/button';

const slides = [
  { src: '/generated/design-references/realistic-local-01.webp', title: 'Contemporary Elegance', copy: 'Warm timber, stone textures and layered lighting for a premium family home.' },
  { src: '/generated/design-references/realistic-local-02.webp', title: 'Modern Minimalist', copy: 'Clean geometry, generous glazing and a calm contemporary facade.' },
  { src: '/generated/design-references/realistic-local-03.webp', title: 'Architectural Harmony', copy: 'Balanced volumes, landscaped edges and refined exterior detailing.' },
];

export function HomeDesignReferenceSlider() {
  const pathname = usePathname();
  const [index,setIndex] = useState(0);
  useEffect(()=>{ if(pathname!=='/') return; const timer=window.setInterval(()=>setIndex(i=>(i+1)%slides.length),6000); return()=>window.clearInterval(timer); },[pathname]);
  if(pathname!=='/') return null;
  const slide=slides[index];
  const go=(next:number)=>setIndex((next+slides.length)%slides.length);
  return <section className="bg-secondary py-20 md:py-24"><div className="section-shell"><div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between"><div className="max-w-3xl"><p className="eyebrow">House design inspiration</p><h2 className="display-title mt-4 text-4xl sm:text-5xl">{slide.title}. Explore the look you love.</h2><p className="mt-5 max-w-2xl text-base leading-8 text-muted-foreground">{slide.copy} These are original concept references, not completed project records.</p></div><Button asChild variant="outline" className="rounded-xl"><Link href="/design-reference">View all references <ArrowRight className="ml-2 h-4 w-4"/></Link></Button></div><div className="mt-10 overflow-hidden rounded-3xl border bg-[#0d1724] shadow-xl"><div className="grid lg:grid-cols-[0.62fr_1.38fr]"><div className="flex flex-col justify-between p-7 text-white sm:p-10 md:p-12"><div><div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary"><Images className="h-6 w-6"/></div><p className="mt-7 text-sm font-semibold uppercase tracking-[0.18em] text-primary">Original concept · {String(index+1).padStart(2,'0')} / {String(slides.length).padStart(2,'0')}</p><h3 className="mt-4 text-2xl font-semibold sm:text-3xl">{slide.title}</h3><p className="mt-3 max-w-md text-sm leading-7 text-white/65 sm:text-base">Use the references to discuss facade style, proportions, materials, landscaping and lighting before a real project is created.</p></div><div className="mt-10 flex items-center gap-3"><button type="button" onClick={()=>go(index-1)} className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/15 text-white transition hover:border-primary hover:text-primary" aria-label="Previous design reference"><ArrowLeft className="h-5 w-5"/></button><button type="button" onClick={()=>go(index+1)} className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/15 text-white transition hover:border-primary hover:text-primary" aria-label="Next design reference"><ArrowRight className="h-5 w-5"/></button><div className="ml-2 flex gap-2">{slides.map((item,dot)=><button key={item.src} type="button" onClick={()=>setIndex(dot)} aria-label={`Show ${item.title}`} className={`h-2.5 rounded-full transition-all ${dot===index?'w-8 bg-primary':'w-2.5 bg-white/25'}`}/>)}</div></div></div><div className="min-h-[380px] bg-white/5 p-3 sm:p-5 md:min-h-[480px]"><div className="h-full overflow-hidden rounded-2xl border border-white/10 bg-white p-2"><img src={slide.src} alt={slide.title} loading={index===0?'eager':'lazy'} decoding="async" className="h-full min-h-[360px] w-full rounded-xl object-cover md:min-h-[460px]"/></div></div></div></div></div></section>;
}

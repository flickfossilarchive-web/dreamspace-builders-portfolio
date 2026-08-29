'use client';

import Link from 'next/link';
import { ArrowRight, Building2, CheckCircle2, Clock3, DraftingCompass, Hammer, Layers3, MessageCircle, Palette, PenTool, Ruler, ShieldCheck, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ProjectCard } from '@/components/project-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { HomeDesignShowcase } from '@/components/home-design-showcase';
import { useCollection, useFirestore } from '@/firebase';
import type { Project } from '@/lib/types';
import { collection, limit, query, where } from 'firebase/firestore';
import { useMemo } from 'react';

const services = [
  { icon: Building2, title: 'Building Construction', description: 'Residential, commercial and industrial construction delivered with disciplined execution.' },
  { icon: Ruler, title: 'Planning & Estimation', description: 'Clear scope, practical planning and detailed estimates before work begins.' },
  { icon: DraftingCompass, title: 'Architecture & Drafting', description: 'Buildable concepts, drawings and technical support aligned to your vision.' },
  { icon: Hammer, title: 'Contracting & Execution', description: 'Coordinated execution from foundation through finishing and handover.' },
  { icon: Users, title: 'Site Supervision', description: 'Ongoing coordination focused on quality, specifications and progress.' },
  { icon: Palette, title: 'Interior Design', description: 'Functional, elegant interiors designed around how you actually use a space.' },
  { icon: PenTool, title: 'Consulting', description: 'Straightforward guidance for material, budget, planning and execution decisions.' },
  { icon: Layers3, title: 'Turnkey Projects', description: 'One accountable team for planning, construction, interiors and completion.' },
];

const reasons = [
  ['One accountable team', 'Fewer handoffs from planning and estimation through execution and finishing.', Layers3],
  ['Clear project planning', 'Know the scope, decisions and next step before work moves forward.', Ruler],
  ['Quality at every stage', 'A consistent focus on workmanship, materials and finishing details.', ShieldCheck],
];

const process = [
  ['01', 'Understand', 'We start with your requirement, site, priorities and preferred outcome.'],
  ['02', 'Design & Estimate', 'We shape the solution and make the scope and cost easier to understand.'],
  ['03', 'Build', 'We coordinate execution, supervision and communication throughout the work.'],
  ['04', 'Handover', 'We complete the work with a clear path to the finished space.'],
];

const trustPoints = [
  ['Quality-led workmanship', 'Thoughtful execution and attention to detail.', ShieldCheck],
  ['Coordinated delivery', 'One team across planning and execution.', Users],
  ['Clear next steps', 'A process you can understand from day one.', Ruler],
  ['Easy to reach', 'Call, email or message when you need us.', MessageCircle],
];

export default function Home() {
  const firestore = useFirestore();
  const projectsQuery = useMemo(() => {
    if (!firestore) return null;
    return query(collection(firestore, 'projects'), where('featured', '==', true), limit(3));
  }, [firestore]);
  const { data: featuredProjects, loading } = useCollection<Project>(projectsQuery);

  return (
    <div className="flex flex-col bg-background">
      <HomeDesignShowcase />

      <section className="section-shell relative z-20 -mt-8 pb-16 md:-mt-10 md:pb-20">
        <div className="grid overflow-hidden rounded-2xl border border-border bg-white shadow-xl shadow-black/10 sm:grid-cols-2 lg:grid-cols-4">
          {trustPoints.map(([title, copy, Icon], index) => (
            <div key={String(title)} className={`flex gap-4 p-6 ${index !== trustPoints.length - 1 ? 'border-b sm:border-b-0 lg:border-r' : ''}`}>
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#08121f] text-primary"><Icon className="h-5 w-5" /></div>
              <div><p className="font-semibold text-[#08121f]">{title}</p><p className="mt-1 text-sm leading-5 text-slate-500">{copy}</p></div>
            </div>
          ))}
        </div>
      </section>

      <section className="section-shell pb-24 md:pb-32">
        <div className="grid gap-12 lg:grid-cols-[0.78fr_1.22fr] lg:gap-20">
          <div>
            <p className="eyebrow">Why Dreamspace</p>
            <h2 className="display-title mt-4 text-4xl sm:text-5xl">A simpler way to build.</h2>
            <div className="gold-line mt-6" />
            <p className="mt-6 max-w-xl text-base leading-8 text-muted-foreground">You should know what is being planned, what the scope includes and what happens next. We keep the process clear from the first conversation to handover.</p>
            <Button asChild variant="outline" className="mt-8 rounded-xl"><Link href="/about">Discover our approach <ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
          </div>
          <div className="grid gap-5 md:grid-cols-3">
            {reasons.map(([title, copy, Icon]) => (
              <Card key={String(title)} className="luxury-card bg-card p-2">
                <CardHeader className="pb-2"><div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary"><Icon className="h-6 w-6" /></div><CardTitle className="pt-3 text-xl">{title}</CardTitle></CardHeader>
                <CardContent className="text-sm leading-6 text-muted-foreground">{copy}</CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-[#101b29] py-24 text-white md:py-28">
        <div className="section-shell">
          <div className="max-w-3xl"><p className="eyebrow text-primary">What we do</p><h2 className="display-title mt-4 text-4xl text-white sm:text-5xl">One team for the full project.</h2><p className="mt-5 text-base leading-8 text-white/65 sm:text-lg">Practical services across planning, design, construction, supervision and finishing.</p></div>
          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {services.map(({ icon: Icon, title, description }) => (
              <div key={title} className="group rounded-2xl border border-white/10 bg-white/[0.04] p-6 transition-all duration-300 hover:-translate-y-1 hover:border-primary/40 hover:bg-white/[0.07]">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-[#101b29]"><Icon className="h-6 w-6" /></div>
                <h3 className="mt-6 text-lg font-semibold text-white">{title}</h3><p className="mt-3 text-sm leading-6 text-white/60">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section-shell py-24 md:py-28">
        <div className="grid gap-12 lg:grid-cols-[0.72fr_1.28fr] lg:gap-20">
          <div><p className="eyebrow">How it works</p><h2 className="display-title mt-4 text-4xl sm:text-5xl">A clear path from idea to handover.</h2><p className="mt-6 text-base leading-8 text-muted-foreground">A straightforward process keeps decisions visible and the next step easy to understand.</p></div>
          <div className="grid gap-4 sm:grid-cols-2">
            {process.map(([number, title, copy]) => (
              <Card key={number} className="luxury-card p-2"><CardContent className="p-7"><div className="flex items-center justify-between"><span className="text-sm font-bold tracking-[0.2em] text-primary">{number}</span><Clock3 className="h-5 w-5 text-muted-foreground" /></div><h3 className="mt-8 text-xl font-semibold">{title}</h3><p className="mt-3 text-sm leading-6 text-muted-foreground">{copy}</p></CardContent></Card>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-secondary py-24 md:py-28">
        <div className="section-shell">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div><p className="eyebrow">Portfolio</p><h2 className="display-title mt-4 text-4xl sm:text-5xl">Selected work.</h2><p className="mt-4 max-w-2xl text-base leading-7 text-muted-foreground">Only completed and admin-published projects appear here.</p></div>
            <Button asChild variant="outline" className="rounded-xl"><Link href="/projects">View all projects <ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
          </div>
          <div className="mt-12">
            {loading ? (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">{[1,2,3].map((item)=><Card key={item} className="overflow-hidden rounded-2xl"><div className="aspect-[4/3] animate-pulse bg-muted"/><div className="space-y-3 p-6"><div className="h-5 w-2/3 animate-pulse rounded bg-muted"/><div className="h-4 w-full animate-pulse rounded bg-muted"/></div></Card>)}</div>
            ) : featuredProjects && featuredProjects.length ? (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">{featuredProjects.map(project => <ProjectCard key={project.id} project={project} />)}</div>
            ) : (
              <div className="rounded-2xl border border-dashed bg-background/70 px-6 py-16 text-center"><Building2 className="mx-auto h-10 w-10 text-primary"/><h3 className="mt-5 text-2xl font-semibold">Our portfolio is being updated</h3><p className="mx-auto mt-3 max-w-xl text-muted-foreground">Completed projects will appear here as they are published through the admin portal.</p><Button asChild className="mt-7 rounded-xl"><Link href="/contact">Discuss your project <ArrowRight className="ml-2 h-4 w-4"/></Link></Button></div>
            )}
          </div>
        </div>
      </section>

      <section className="section-shell py-24 md:py-28">
        <div className="relative overflow-hidden rounded-3xl bg-[#0d1724] px-7 py-14 text-white shadow-2xl sm:px-12 md:px-16 md:py-16"><div className="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-primary/15 blur-3xl"/><div className="relative z-10 flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between"><div className="max-w-2xl"><p className="eyebrow text-primary">Let’s build it right</p><h2 className="display-title mt-4 text-4xl text-white sm:text-5xl">Have a project in mind?</h2><p className="mt-5 text-base leading-7 text-white/65 sm:text-lg">Share your idea, location and approximate scope. We’ll help you understand the next step.</p></div><Button asChild size="lg" className="h-14 rounded-xl bg-primary px-7 text-base font-bold text-[#0d1724] hover:bg-primary/90"><Link href="/contact">Start a conversation <ArrowRight className="ml-2 h-5 w-5"/></Link></Button></div></div>
      </section>
    </div>
  );
}

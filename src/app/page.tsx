'use client';

import Link from 'next/link';
import { useMemo } from 'react';
import {
  ArrowRight,
  Building2,
  CheckCircle2,
  Clock3,
  DraftingCompass,
  Hammer,
  Layers3,
  Mail,
  MapPin,
  MessageCircle,
  Palette,
  PenTool,
  Ruler,
  ShieldCheck,
  Sparkles,
  Users,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ProjectCard } from '@/components/project-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import placeholderImages from '@/lib/placeholder-images.json';
import Image from 'next/image';
import { useCollection, useFirestore } from '@/firebase';
import type { Project } from '@/lib/types';
import { collection, query, where, limit } from 'firebase/firestore';

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
  ['Clear communication', 'You always know what is being planned, built and completed next.', MessageCircle],
  ['Quality-first execution', 'We focus on workmanship, materials and attention to detail at every stage.', ShieldCheck],
  ['End-to-end capability', 'From concept and estimate to execution and interiors, fewer handoffs mean better coordination.', Layers3],
];

const process = [
  ['01', 'Plan', 'Understand your requirement, site, scope and priorities.'],
  ['02', 'Design & Estimate', 'Shape the solution and make the cost and scope easier to understand.'],
  ['03', 'Build', 'Execute with coordination, supervision and regular communication.'],
  ['04', 'Handover', 'Complete the work with a clear path to the finished space.'],
];

export default function Home() {
  const { hero } = placeholderImages;
  const firestore = useFirestore();
  const projectsQuery = useMemo(() => {
    if (!firestore) return null;
    return query(collection(firestore, 'projects'), where('featured', '==', true), limit(3));
  }, [firestore]);

  const { data: featuredProjects, loading } = useCollection<Project>(projectsQuery);

  return (
    <div className="flex flex-col bg-background">
      <section className="relative isolate min-h-[720px] overflow-hidden bg-[#0d1724] text-white">
        <Image
          src={hero.src}
          alt={hero.alt}
          fill
          priority
          sizes="100vw"
          className="object-cover object-center"
        />
        <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(7,15,25,0.9)_0%,rgba(7,15,25,0.72)_40%,rgba(7,15,25,0.25)_75%,rgba(7,15,25,0.12)_100%)]" />
        <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(7,15,25,0.12)_0%,rgba(7,15,25,0.05)_45%,rgba(7,15,25,0.9)_100%)]" />
        <div className="absolute inset-0 opacity-20 [background-image:linear-gradient(rgba(255,255,255,0.12)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.12)_1px,transparent_1px)] [background-size:72px_72px] [mask-image:linear-gradient(to_bottom,black,transparent_72%)]" />

        <div className="section-shell relative z-10 flex min-h-[720px] items-end pb-16 pt-28 md:pb-24">
          <div className="max-w-4xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-white/85 backdrop-blur-sm">
              <Sparkles className="h-4 w-4 text-primary" /> Construction & design · Davanagere
            </div>
            <h1 className="display-title mt-7 max-w-4xl text-5xl leading-[0.98] text-white sm:text-6xl md:text-7xl lg:text-8xl">
              Building spaces.
              <span className="block text-white/90">Creating legacies.</span>
            </h1>
            <p className="mt-7 max-w-2xl text-base leading-7 text-white/78 sm:text-lg sm:leading-8">
              From concept and estimation to construction, supervision and interiors, Dreamspace Builders brings the whole project together under one roof.
            </p>

            <div className="mt-10 flex flex-col gap-3 sm:flex-row">
              <Button asChild size="lg" className="h-14 rounded-xl bg-primary px-7 text-base font-bold shadow-2xl shadow-black/20 hover:bg-primary/90">
                <Link href="/contact">Get a project estimate <ArrowRight className="ml-2 h-5 w-5" /></Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="h-14 rounded-xl border-white/40 bg-white/5 px-7 text-base font-bold text-white backdrop-blur-sm hover:bg-white hover:text-[#0d1724]">
                <Link href="/projects">View our work</Link>
              </Button>
            </div>

            <div className="mt-9 flex flex-wrap gap-5 text-sm text-white/75">
              {['Residential', 'Commercial', 'Industrial', 'Turnkey'].map((item) => (
                <span key={item} className="inline-flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary" /> {item}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="section-shell absolute bottom-0 left-0 right-0 z-20 translate-y-1/2">
          <div className="grid grid-cols-1 overflow-hidden rounded-2xl border border-white/70 bg-white shadow-2xl shadow-black/10 sm:grid-cols-2 lg:grid-cols-4">
            {[
              ['Quality focused', 'Thoughtful workmanship and materials.', ShieldCheck],
              ['Experienced coordination', 'One team across planning and execution.', Users],
              ['Clear process', 'Understand what happens next.', Ruler],
              ['Client-first support', 'Easy ways to call, message or enquire.', MessageCircle],
            ].map(([title, copy, Icon], index) => (
              <div key={String(title)} className={`flex gap-4 p-6 ${index !== 3 ? 'border-b sm:border-b-0 lg:border-r' : ''}`}>
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#0d1724] text-primary">
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <p className="font-semibold text-[#0d1724]">{title}</p>
                  <p className="mt-1 text-sm leading-5 text-slate-500">{copy}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section-shell pt-36 pb-24 md:pt-40 md:pb-32">
        <div className="grid gap-12 lg:grid-cols-[0.8fr_1.2fr] lg:gap-20">
          <div>
            <p className="eyebrow">Why Dreamspace</p>
            <h2 className="display-title mt-4 text-4xl sm:text-5xl">Your vision.<br />Our commitment.</h2>
            <div className="gold-line mt-6" />
            <p className="mt-6 max-w-xl text-base leading-8 text-muted-foreground">
              Good construction is not only about the finished structure. It is about making the journey clearer, the decisions easier and the execution more dependable.
            </p>
            <Button asChild variant="outline" className="mt-8 rounded-xl px-5">
              <Link href="/about">Discover our approach <ArrowRight className="ml-2 h-4 w-4" /></Link>
            </Button>
          </div>

          <div className="grid gap-5 md:grid-cols-3">
            {reasons.map(([title, copy, Icon]) => (
              <Card key={String(title)} className="luxury-card bg-card p-2">
                <CardHeader className="pb-2">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <Icon className="h-6 w-6" />
                  </div>
                  <CardTitle className="pt-3 text-xl">{title}</CardTitle>
                </CardHeader>
                <CardContent className="text-sm leading-6 text-muted-foreground">{copy}</CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-[#101b29] py-24 text-white md:py-28">
        <div className="section-shell">
          <div className="max-w-3xl">
            <p className="eyebrow text-primary">Services</p>
            <h2 className="display-title mt-4 text-4xl text-white sm:text-5xl">One team for the full project.</h2>
            <p className="mt-5 text-base leading-8 text-white/65 sm:text-lg">Practical services that cover the stages that matter most—planning, design, construction, supervision and finishing.</p>
          </div>

          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {services.map(({ icon: Icon, title, description }) => (
              <div key={title} className="group rounded-2xl border border-white/10 bg-white/[0.04] p-6 transition-all duration-300 hover:-translate-y-1 hover:border-primary/40 hover:bg-white/[0.07]">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-[#101b29]">
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="mt-6 text-lg font-semibold text-white">{title}</h3>
                <p className="mt-3 text-sm leading-6 text-white/60">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section-shell py-24 md:py-28">
        <div className="grid gap-12 lg:grid-cols-[0.72fr_1.28fr] lg:items-start lg:gap-20">
          <div>
            <p className="eyebrow">How it works</p>
            <h2 className="display-title mt-4 text-4xl sm:text-5xl">A clearer path from idea to handover.</h2>
            <p className="mt-6 text-base leading-8 text-muted-foreground">A simple process helps you understand the next step without getting buried in construction jargon.</p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {process.map(([number, title, copy]) => (
              <Card key={number} className="luxury-card p-2">
                <CardContent className="p-7">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold tracking-[0.2em] text-primary">{number}</span>
                    <Clock3 className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <h3 className="mt-8 text-xl font-semibold">{title}</h3>
                  <p className="mt-3 text-sm leading-6 text-muted-foreground">{copy}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-secondary py-24 md:py-28">
        <div className="section-shell">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="eyebrow">Portfolio</p>
              <h2 className="display-title mt-4 text-4xl sm:text-5xl">Selected work.</h2>
              <p className="mt-4 max-w-2xl text-base leading-7 text-muted-foreground">Explore completed and featured projects by category and see how we approach different kinds of spaces.</p>
            </div>
            <Button asChild variant="outline" className="rounded-xl">
              <Link href="/projects">View all projects <ArrowRight className="ml-2 h-4 w-4" /></Link>
            </Button>
          </div>

          <div className="mt-12">
            {loading ? (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {[1, 2, 3].map((item) => <Card key={item} className="overflow-hidden rounded-2xl"><div className="aspect-[4/3] animate-pulse bg-muted" /><div className="space-y-3 p-6"><div className="h-5 w-2/3 animate-pulse rounded bg-muted" /><div className="h-4 w-full animate-pulse rounded bg-muted" /></div></Card>)}
              </div>
            ) : featuredProjects && featuredProjects.length > 0 ? (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {featuredProjects.map((project) => <ProjectCard key={project.id} project={project} />)}
              </div>
            ) : (
              <div className="rounded-2xl border border-dashed bg-background/70 px-6 py-16 text-center">
                <Building2 className="mx-auto h-10 w-10 text-primary" />
                <h3 className="mt-5 text-2xl font-semibold">Our portfolio is being updated</h3>
                <p className="mx-auto mt-3 max-w-xl text-muted-foreground">We’re updating the showcase. Contact us to discuss your requirement or ask about recent work.</p>
                <Button asChild className="mt-7 rounded-xl"><Link href="/contact">Start a conversation <ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="section-shell py-24 md:py-28">
        <div className="relative overflow-hidden rounded-3xl bg-[#0d1724] px-7 py-14 text-white shadow-2xl sm:px-12 md:px-16 md:py-16">
          <div className="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-primary/15 blur-3xl" />
          <div className="relative z-10 flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl">
              <p className="eyebrow text-primary">Let’s build it right</p>
              <h2 className="display-title mt-4 text-4xl text-white sm:text-5xl">Have a project in mind?</h2>
              <p className="mt-5 text-base leading-7 text-white/65 sm:text-lg">Share your idea, location and approximate scope. We’ll help you understand the next step.</p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Button asChild size="lg" className="h-14 rounded-xl bg-primary px-7 font-bold hover:bg-primary/90">
                <Link href="/contact">Request a quote <ArrowRight className="ml-2 h-5 w-5" /></Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="h-14 rounded-xl border-white/25 bg-white/5 px-7 font-bold text-white hover:bg-white hover:text-[#0d1724]">
                <a href="https://wa.me/919008592532" target="_blank" rel="noreferrer"><MessageCircle className="mr-2 h-5 w-5" /> WhatsApp</a>
              </Button>
            </div>
          </div>
        </div>
      </section>

      <section className="border-t bg-background py-8">
        <div className="section-shell flex flex-col gap-4 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4">
            <span className="inline-flex items-center gap-2"><MapPin className="h-4 w-4 text-primary" /> Davanagere, Karnataka</span>
            <a href="mailto:Dreamspacebuilders12@gmail.com" className="hidden items-center gap-2 hover:text-primary sm:inline-flex"><Mail className="h-4 w-4 text-primary" /> Email us</a>
          </div>
          <Link href="/contact" className="font-semibold text-foreground hover:text-primary">Start your project <ArrowRight className="ml-1 inline h-4 w-4" /></Link>
        </div>
      </section>
    </div>
  );
}

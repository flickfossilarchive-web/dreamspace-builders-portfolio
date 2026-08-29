'use client';

import { useEffect, useMemo, useState } from 'react';
import { Search, ArrowRight, FolderOpen, Loader2 } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import { Input } from '@/components/ui/input';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ProjectCard } from '@/components/project-card';
import type { Project } from '@/lib/types';
import { useCollection, useFirestore } from '@/firebase';
import { collection } from 'firebase/firestore';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

const categories = ['All', 'Commercial', 'Residential', 'Industrial'];

export default function ProjectsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  const [additionalGallerySrc, setAdditionalGallerySrc] = useState<string | null>(null);
  const firestore = useFirestore();
  const projectsCollection = useMemo(() => firestore ? collection(firestore, 'projects') : null, [firestore]);
  const { data: projects, loading } = useCollection<Project>(projectsCollection);

  useEffect(() => {
    let active = true;
    fetch('/house-designs/residential-design-gallery-more.b64', { cache: 'force-cache' })
      .then((response) => response.ok ? response.text() : '')
      .then((base64) => {
        if (active && base64.trim()) setAdditionalGallerySrc(`data:image/webp;base64,${base64.trim()}`);
      })
      .catch(() => undefined);
    return () => { active = false; };
  }, []);

  const filteredProjects = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();
    if (!projects) return [];
    return projects.filter((project) => {
      const visible = project.visible !== false;
      const matchesCategory = activeCategory === 'All' || project.category === activeCategory;
      const searchable = [project.title, project.description, project.location, project.scope, ...(project.tags ?? [])].filter(Boolean).join(' ').toLowerCase();
      return visible && matchesCategory && (!normalizedSearch || searchable.includes(normalizedSearch));
    });
  }, [projects, searchTerm, activeCategory]);

  return (
    <div className="bg-background">
      <section className="bg-[#0d1724] py-20 text-white md:py-28"><div className="section-shell"><p className="eyebrow text-primary">Portfolio</p><h1 className="display-title mt-4 max-w-4xl text-5xl text-white sm:text-6xl md:text-7xl">Selected work, thoughtfully built.</h1><p className="mt-6 max-w-2xl text-base leading-8 text-white/65 sm:text-lg">Explore projects by type and see the range of spaces Dreamspace Builders can help plan, build and complete.</p></div></section>
      <section className="section-shell py-16 md:py-24">
        <div className="rounded-2xl border bg-secondary/60 p-4 md:p-5"><div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between"><div className="relative w-full lg:max-w-md"><Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" /><Input type="search" placeholder="Search projects..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="h-12 rounded-xl bg-background pl-10" aria-label="Search projects" /></div><Tabs value={activeCategory} onValueChange={setActiveCategory}><TabsList className="grid w-full grid-cols-2 rounded-xl sm:grid-cols-4 lg:w-auto">{categories.map((category) => <TabsTrigger key={category} value={category}>{category}</TabsTrigger>)}</TabsList></Tabs></div></div>

        <section className="mt-14 rounded-3xl border bg-[#0d1724] p-5 text-white shadow-xl sm:p-8 md:mt-16 md:p-10">
          <div className="grid items-center gap-8 lg:grid-cols-[0.75fr_1.25fr] lg:gap-12">
            <div>
              <p className="eyebrow text-primary">Residential design collection</p>
              <h2 className="display-title mt-4 text-3xl text-white sm:text-4xl">House designs with a strong sense of place.</h2>
              <p className="mt-5 max-w-xl text-sm leading-7 text-white/65 sm:text-base">A curated selection of residential design visuals shared by the client, showcasing contemporary facades, planning ideas and different architectural directions.</p>
              <div className="mt-6 flex flex-wrap gap-3 text-xs font-semibold uppercase tracking-[0.14em] text-white/55">
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-2">Residential</span>
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-2">Design concepts</span>
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-2">9 visuals</span>
              </div>
              <Button asChild className="mt-8 rounded-xl bg-primary font-bold text-[#0d1724] hover:bg-primary/90"><Link href="/contact">Discuss a house design <ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
            </div>
            <div className="overflow-hidden rounded-2xl border border-white/10 bg-white/5">
              <Image src="/house-designs/residential-design-gallery.webp" alt="Residential house design collection featuring contemporary facade concepts" width={1332} height={972} sizes="(max-width: 1024px) 100vw, 60vw" className="h-auto w-full object-cover" />
            </div>
          </div>
        </section>

        {additionalGallerySrc && (
          <section className="mt-8 overflow-hidden rounded-3xl border bg-white shadow-lg">
            <div className="grid items-center gap-0 lg:grid-cols-[0.75fr_1.25fr]">
              <div className="p-6 sm:p-8 md:p-10">
                <p className="eyebrow">More residential references</p>
                <h2 className="display-title mt-4 text-3xl sm:text-4xl">More facade directions to explore.</h2>
                <p className="mt-5 max-w-xl text-sm leading-7 text-muted-foreground sm:text-base">A second set of residential design visuals shared by the client, showing alternate facade compositions, materials and massing ideas.</p>
                <div className="mt-6 flex flex-wrap gap-3 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                  <span className="rounded-full border bg-secondary px-3 py-2">4 additional visuals</span>
                  <span className="rounded-full border bg-secondary px-3 py-2">Residential</span>
                  <span className="rounded-full border bg-secondary px-3 py-2">Facade concepts</span>
                </div>
                <Button asChild variant="outline" className="mt-8 rounded-xl"><Link href="/contact">Talk about your design <ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
              </div>
              <div className="bg-[#0d1724] p-4 sm:p-6">
                <img src={additionalGallerySrc} alt="Additional residential house design references featuring modern facades and architectural forms" width="1200" height="820" loading="lazy" decoding="async" className="h-auto w-full rounded-2xl object-cover" />
              </div>
            </div>
          </section>
        )}

        <div className="mt-10" aria-busy={loading}>
          {loading ? (
            <Card className="rounded-2xl border bg-card shadow-sm">
              <CardContent className="flex min-h-64 flex-col items-center justify-center px-6 py-16 text-center">
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10"><Loader2 className="h-7 w-7 animate-spin text-primary" aria-hidden="true" /></div>
                <h2 className="mt-5 text-2xl font-semibold">Loading our projects</h2>
                <p className="mx-auto mt-3 max-w-xl text-muted-foreground">We are loading the latest portfolio entries. You can search or filter them as soon as they are available.</p>
              </CardContent>
            </Card>
          ) : filteredProjects.length > 0 ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">{filteredProjects.map(project => <ProjectCard key={project.id} project={project} />)}</div>
          ) : (
            <Card className="rounded-2xl border-dashed"><CardContent className="px-6 py-20 text-center"><FolderOpen className="mx-auto h-10 w-10 text-primary" /><h2 className="mt-5 text-2xl font-semibold">No matching projects</h2><p className="mx-auto mt-3 max-w-xl text-muted-foreground">Try another keyword or browse all categories. You can also contact us to discuss a project similar to what you have in mind.</p><Button asChild className="mt-7 rounded-xl"><Link href="/contact">Discuss your project <ArrowRight className="ml-2 h-4 w-4" /></Link></Button></CardContent></Card>
          )}
        </div>
      </section>
    </div>
  );
}

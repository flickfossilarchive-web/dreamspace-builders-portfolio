'use client';

import { useMemo, useState } from 'react';
import { Search, ArrowRight, FolderOpen, Loader2 } from 'lucide-react';
import Link from 'next/link';
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
  const firestore = useFirestore();
  const projectsCollection = useMemo(() => (firestore ? collection(firestore, 'projects') : null), [firestore]);
  const { data: projects, loading } = useCollection<Project>(projectsCollection);

  const filteredProjects = useMemo(() => {
    const normalized = searchTerm.trim().toLowerCase();
    if (!projects) return [];
    return projects.filter((project) => {
      const visible = project.visible !== false;
      const matchesCategory = activeCategory === 'All' || project.category === activeCategory;
      const searchable = [project.title, project.description, project.location, project.scope, project.overview, ...(project.tags ?? [])].filter(Boolean).join(' ').toLowerCase();
      return visible && matchesCategory && (!normalized || searchable.includes(normalized));
    });
  }, [projects, searchTerm, activeCategory]);

  return (
    <div className="bg-background">
      <section className="bg-[#0d1724] py-20 text-white md:py-28">
        <div className="section-shell">
          <p className="eyebrow text-primary">Portfolio</p>
          <h1 className="display-title mt-4 max-w-4xl text-5xl text-white sm:text-6xl md:text-7xl">Selected work, thoughtfully built.</h1>
          <p className="mt-6 max-w-2xl text-base leading-8 text-white/65 sm:text-lg">Explore completed and published projects by Dreamspace Builders. New project details are added and maintained by the admin team.</p>
        </div>
      </section>

      <section className="section-shell py-16 md:py-24">
        <div className="rounded-2xl border bg-secondary/60 p-4 md:p-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="relative w-full lg:max-w-md">
              <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
              <Input type="search" placeholder="Search projects..." value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} className="h-12 rounded-xl bg-background pl-10" aria-label="Search projects" />
            </div>
            <Tabs value={activeCategory} onValueChange={setActiveCategory}>
              <TabsList className="grid w-full grid-cols-2 rounded-xl sm:grid-cols-4 lg:w-auto">
                {categories.map((category) => <TabsTrigger key={category} value={category}>{category}</TabsTrigger>)}
              </TabsList>
            </Tabs>
          </div>
        </div>

        <div className="mt-12">
          {loading ? (
            <Card className="rounded-2xl"><CardContent className="flex min-h-64 flex-col items-center justify-center px-6 py-16 text-center"><div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10"><Loader2 className="h-7 w-7 animate-spin text-primary" aria-hidden="true" /></div><h2 className="mt-5 text-2xl font-semibold">Loading published projects</h2><p className="mx-auto mt-3 max-w-xl text-muted-foreground">Published projects will appear here once the portfolio data is available.</p></CardContent></Card>
          ) : filteredProjects.length > 0 ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">{filteredProjects.map((project) => <ProjectCard key={project.id} project={project} />)}</div>
          ) : (
            <Card className="rounded-2xl border-dashed"><CardContent className="px-6 py-20 text-center"><FolderOpen className="mx-auto h-10 w-10 text-primary" /><h2 className="mt-5 text-2xl font-semibold">No published projects yet</h2><p className="mx-auto mt-3 max-w-xl text-muted-foreground">We are preparing the portfolio. Design inspiration is available separately, while completed project details are published by the admin team.</p><div className="mt-7 flex flex-col justify-center gap-3 sm:flex-row"><Button asChild className="rounded-xl"><Link href="/design-reference">Browse design references <ArrowRight className="ml-2 h-4 w-4" /></Link></Button><Button asChild variant="outline" className="rounded-xl"><Link href="/contact">Discuss your project</Link></Button></div></CardContent></Card>
          )}
        </div>
      </section>
    </div>
  );
}

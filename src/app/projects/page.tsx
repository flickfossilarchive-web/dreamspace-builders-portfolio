'use client';

import { useMemo, useState } from 'react';
import { Search, ArrowRight, FolderOpen } from 'lucide-react';
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
  const projectsCollection = useMemo(() => firestore ? collection(firestore, 'projects') : null, [firestore]);
  const { data: projects, loading } = useCollection<Project>(projectsCollection);

  const filteredProjects = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();
    if (!projects) return [];
    return projects.filter((project) => {
      const matchesCategory = activeCategory === 'All' || project.category === activeCategory;
      const searchable = [project.title, project.description, ...(project.tags ?? [])].join(' ').toLowerCase();
      return matchesCategory && (!normalizedSearch || searchable.includes(normalizedSearch));
    });
  }, [projects, searchTerm, activeCategory]);

  return (
    <div className="bg-background">
      <section className="bg-[#0d1724] py-20 text-white md:py-28">
        <div className="section-shell">
          <p className="eyebrow text-primary">Portfolio</p>
          <h1 className="display-title mt-4 max-w-4xl text-5xl text-white sm:text-6xl md:text-7xl">Selected work, thoughtfully built.</h1>
          <p className="mt-6 max-w-2xl text-base leading-8 text-white/65 sm:text-lg">Explore projects by type and see the range of spaces Dreamspace Builders can help plan, build and complete.</p>
        </div>
      </section>

      <section className="section-shell py-16 md:py-24">
        <div className="rounded-2xl border bg-secondary/60 p-4 md:p-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="relative w-full lg:max-w-md">
              <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
              <Input type="search" placeholder="Search projects..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="h-12 rounded-xl bg-background pl-10" />
            </div>
            <Tabs value={activeCategory} onValueChange={setActiveCategory}>
              <TabsList className="grid w-full grid-cols-2 rounded-xl sm:grid-cols-4 lg:w-auto">
                {categories.map((category) => <TabsTrigger key={category} value={category}>{category}</TabsTrigger>)}
              </TabsList>
            </Tabs>
          </div>
        </div>

        <div className="mt-10">
          {loading ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3, 4, 5, 6].map((item) => (
                <Card key={item} className="overflow-hidden rounded-2xl"><div className="aspect-[4/3] animate-pulse bg-muted" /><div className="space-y-3 p-6"><div className="h-5 w-2/3 animate-pulse rounded bg-muted" /><div className="h-4 w-full animate-pulse rounded bg-muted" /></div></Card>
              ))}
            </div>
          ) : filteredProjects.length > 0 ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filteredProjects.map((project) => <ProjectCard key={project.id} project={project} />)}
            </div>
          ) : (
            <Card className="rounded-2xl border-dashed">
              <CardContent className="px-6 py-20 text-center">
                <FolderOpen className="mx-auto h-10 w-10 text-primary" />
                <h2 className="mt-5 text-2xl font-semibold">No matching projects</h2>
                <p className="mx-auto mt-3 max-w-xl text-muted-foreground">Try another keyword or browse all categories. You can also contact us to discuss a project similar to what you have in mind.</p>
                <Button asChild className="mt-7 rounded-xl"><Link href="/contact">Discuss your project <ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
              </CardContent>
            </Card>
          )}
        </div>
      </section>
    </div>
  );
}

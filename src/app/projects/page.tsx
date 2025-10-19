'use client';

import { useState, useMemo } from 'react';
import { Input } from '@/components/ui/input';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ProjectCard } from '@/components/project-card';
import type { Project } from '@/lib/types';
import { Search } from 'lucide-react';
import { useCollection } from '@/firebase';
import { collection, getFirestore } from 'firebase/firestore';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';

const categories = ['All', 'Commercial', 'Residential', 'Industrial'];

export default function ProjectsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  
  const firestore = useMemo(() => getFirestore(), []);
  const projectsCollection = useMemo(() => {
    if (!firestore) return null;
    return collection(firestore, 'projects');
  }, [firestore]);

  const { data: projects, loading } = useCollection<Project>(projectsCollection);

  const filteredProjects = useMemo(() => {
    if (!projects) return [];
    return projects.filter((project: Project) => {
      const matchesCategory = activeCategory === 'All' || project.category === activeCategory;
      const matchesSearch =
        project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (project.tags && project.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())));
      return matchesCategory && matchesSearch;
    });
  }, [projects, searchTerm, activeCategory]);

  return (
    <div className="container mx-auto px-4 py-16 md:py-24">
      <div className="text-center mb-16">
        <h1 className="text-5xl md:text-6xl font-bold font-headline text-primary">Our Portfolio</h1>
        <p className="mt-4 text-lg text-muted-foreground max-w-3xl mx-auto">
          Explore our diverse range of successfully completed projects, showcasing our commitment to quality and innovation.
        </p>
      </div>

      <div className="flex flex-col md:flex-row gap-6 mb-12 justify-center items-center p-4 bg-secondary rounded-lg border border-border/60">
        <div className="relative w-full md:w-1/2 lg:w-1/3">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search by keyword..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10"
          />
        </div>
        <Tabs value={activeCategory} onValueChange={setActiveCategory} className="w-full md:w-auto">
          <TabsList className="grid w-full grid-cols-2 md:grid-cols-4 md:w-auto">
            {categories.map((category) => (
              <TabsTrigger key={category} value={category}>{category}</TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[...Array(3)].map((_, i) => (
             <Card key={i}><CardHeader><div className="relative aspect-video w-full overflow-hidden bg-muted animate-pulse"></div></CardHeader><CardContent className="space-y-2 mt-6"><div className="h-6 w-3/4 bg-muted animate-pulse rounded-md"></div><div className="h-4 w-full bg-muted animate-pulse rounded-md"></div></CardContent><CardFooter><div className="h-10 w-full bg-muted animate-pulse rounded-md"></div></CardFooter></Card>
          ))}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredProjects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>

          {filteredProjects.length === 0 && (
            <div className="text-center py-24">
                <p className="text-2xl font-semibold text-muted-foreground">No Projects Found</p>
                <p className="mt-3 text-muted-foreground">Try adjusting your search or filter to find what you're looking for.</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

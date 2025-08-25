'use client';

import { useState, useMemo } from 'react';
import { Input } from '@/components/ui/input';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ProjectCard } from '@/components/project-card';
import { projects } from '@/lib/data';
import type { Project } from '@/lib/types';
import { Search } from 'lucide-react';

const categories = ['All', 'Commercial', 'Residential', 'Industrial'];

export default function ProjectsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');

  const filteredProjects = useMemo(() => {
    return projects.filter((project: Project) => {
      const matchesCategory = activeCategory === 'All' || project.category === activeCategory;
      const matchesSearch =
        project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
      return matchesCategory && matchesSearch;
    });
  }, [searchTerm, activeCategory]);

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
    </div>
  );
}

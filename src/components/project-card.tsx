import Image from 'next/image';
import Link from 'next/link';
import type { Project } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowRight } from 'lucide-react';

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Card className="flex flex-col overflow-hidden bg-card border shadow-lg hover:shadow-xl transition-all duration-300 group hover:-translate-y-1">
      <CardHeader className="p-0">
        <div className="relative aspect-video w-full overflow-hidden">
          <Image
            src={project.imageUrl}
            alt={project.title}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-500"
            data-ai-hint={`${project.category.toLowerCase()} ${project.tags && project.tags.length > 0 ? project.tags[0] : ''}`}
          />
           <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
        </div>
      </CardHeader>
      <div className="flex flex-col flex-grow p-6">
        <div className="mb-3">
          <Badge variant="secondary">{project.category}</Badge>
        </div>
        <CardTitle className="font-headline text-xl mb-2">{project.title}</CardTitle>
        <CardDescription className="flex-grow text-muted-foreground">{project.description}</CardDescription>
      </div>
      <CardFooter className="p-6 bg-card/50">
        <Button asChild variant="outline" className="w-full font-semibold">
          <Link href="/contact">
            Contact for Plans <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </CardFooter>
    </Card>
  );
}

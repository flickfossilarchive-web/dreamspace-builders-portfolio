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
    <Card className="flex flex-col overflow-hidden shadow-md hover:shadow-lg transition-shadow duration-300">
      <CardHeader className="p-0">
        <div className="relative aspect-video w-full">
          <Image
            src={project.image}
            alt={project.title}
            fill
            className="object-cover"
            data-ai-hint={`${project.category.toLowerCase()} ${project.tags[0]}`}
          />
        </div>
      </CardHeader>
      <div className="flex flex-col flex-grow p-6">
        <CardTitle className="font-headline text-xl mb-2">{project.title}</CardTitle>
        <div className="mb-4">
          <Badge variant="secondary">{project.category}</Badge>
        </div>
        <CardDescription className="flex-grow text-muted-foreground">{project.description}</CardDescription>
      </div>
      <CardFooter>
        <Button asChild variant="outline" className="w-full">
          <Link href="/contact">
            Contact for Plans <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </CardFooter>
    </Card>
  );
}

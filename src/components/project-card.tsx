import Image from 'next/image';
import Link from 'next/link';
import type { Project } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowUpRight, MapPin } from 'lucide-react';

interface ProjectCardProps { project: Project; }

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Card className="group overflow-hidden rounded-2xl border-0 bg-[#0d1724] text-white shadow-xl transition-transform duration-300 hover:-translate-y-1 hover:shadow-2xl">
      <Link href={`/projects/${project.id}`} className="block" aria-label={`View ${project.title}`}>
        <div className="relative aspect-[4/3] overflow-hidden">
          <Image src={project.imageUrl} alt={project.title} fill sizes="(min-width: 1024px) 33vw, (min-width: 768px) 50vw, 100vw" className="object-cover transition-transform duration-700 group-hover:scale-105" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#07101b] via-transparent to-transparent" />
          <div className="absolute left-5 top-5 flex items-center gap-2"><Badge className="border border-white/20 bg-black/30 text-white backdrop-blur-sm">{project.category}</Badge>{project.status && <Badge className="border border-primary/30 bg-primary/90 text-[#0d1724]">{project.status}</Badge>}</div>
          <div className="absolute bottom-5 left-5 right-5">
            <div className="flex items-center gap-2 text-xs font-medium text-white/75"><MapPin className="h-3.5 w-3.5 text-primary" /> {project.location || 'Davanagere'}</div>
            <h3 className="mt-2 font-headline text-2xl font-bold">{project.title}</h3>
          </div>
        </div>
      </Link>
      <CardContent className="p-6">
        <div className="flex flex-wrap gap-2">{(project.tags ?? []).slice(0, 3).map((tag) => <span key={tag} className="rounded-full bg-white/5 px-3 py-1 text-[11px] font-medium text-white/60">{tag}</span>)}</div>
        <p className="mt-4 line-clamp-3 text-sm leading-6 text-white/65">{project.description}</p>
        <Button asChild variant="ghost" className="mt-5 w-full justify-between rounded-xl border border-white/10 bg-white/5 text-white hover:bg-primary hover:text-[#0d1724]"><Link href={`/projects/${project.id}`}>View project <ArrowUpRight className="h-4 w-4" /></Link></Button>
      </CardContent>
    </Card>
  );
}

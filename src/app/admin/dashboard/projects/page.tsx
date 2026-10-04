'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { ExternalLink, FolderKanban, MapPin, Search, Star } from 'lucide-react';
import { PORTFOLIO_PROJECTS } from '@/data/projects';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';

const projectSourceUrl = 'https://github.com/flickfossilarchive-web/dreamspace-builders-portfolio/blob/main/src/data/projects.ts';

export default function AdminProjectsPage() {
  const [search, setSearch] = useState('');
  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase();
    return PORTFOLIO_PROJECTS.filter((project) => !term || [project.title, project.location, project.category, ...(project.tags ?? [])].filter(Boolean).join(' ').toLowerCase().includes(term));
  }, [search]);

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div><p className="eyebrow">Portfolio management</p><h1 className="mt-2 font-headline text-4xl font-bold tracking-tight">Projects</h1><p className="mt-2 max-w-2xl text-muted-foreground">Project details and images are stored with the site and published through Vercel deployments.</p></div>
        <Button asChild variant="outline" className="rounded-xl"><a href={projectSourceUrl} target="_blank" rel="noreferrer">View project source <ExternalLink className="ml-2 h-4 w-4" /></a></Button>
      </div>
      <div className="flex items-center gap-3 rounded-2xl border bg-secondary/30 p-4"><div className="relative max-w-xl flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by name, location or tag" className="rounded-xl pl-9 bg-background" /></div><span className="hidden text-sm text-muted-foreground sm:inline">{PORTFOLIO_PROJECTS.length} total</span></div>
      {filtered.length ? <div className="grid gap-5 lg:grid-cols-2">{filtered.map((project) => <Card key={project.id} className="overflow-hidden rounded-2xl"><div className="relative aspect-[16/9] bg-muted"><Image src={project.imageUrl} alt={project.title} fill sizes="(min-width: 1024px) 45vw, 100vw" className="object-cover" /><div className="absolute left-4 top-4 flex flex-wrap gap-2"><Badge className="bg-black/65 text-white backdrop-blur">{project.category}</Badge>{project.status && <Badge className="bg-primary text-[#0d1724]">{project.status}</Badge>}{project.featured && <Badge className="bg-white text-[#0d1724]"><Star className="mr-1 h-3 w-3 fill-current" />Featured</Badge>}</div></div><CardContent className="p-5"><div className="flex items-start justify-between gap-4"><div><h2 className="font-headline text-xl font-bold">{project.title}</h2><p className="mt-1 flex items-center gap-1 text-sm text-muted-foreground"><MapPin className="h-3.5 w-3.5" />{project.location}</p></div><span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-800">{project.visible === false ? 'Draft' : 'Published'}</span></div><p className="mt-4 line-clamp-2 text-sm leading-6 text-muted-foreground">{project.description}</p><div className="mt-5 flex flex-wrap gap-2">{(project.tags ?? []).slice(0, 4).map((tag) => <span key={tag} className="rounded-full bg-secondary px-2.5 py-1 text-xs text-secondary-foreground">{tag}</span>)}</div><div className="mt-6"><Button asChild variant="outline" className="rounded-xl"><Link href={`/projects/${project.id}`} target="_blank"><ExternalLink className="mr-2 h-4 w-4" />Preview</Link></Button></div></CardContent></Card>)}</div> : <Card className="rounded-2xl border-dashed"><CardContent className="px-6 py-20 text-center"><FolderKanban className="mx-auto h-10 w-10 text-primary" /><h2 className="mt-5 font-headline text-2xl font-bold">No projects match this search</h2><p className="mx-auto mt-2 max-w-lg text-muted-foreground">Project details are kept in the site source and deployed to Vercel.</p></CardContent></Card>}
    </div>
  );
}
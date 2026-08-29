'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { collection, deleteDoc, doc } from 'firebase/firestore';
import { useCollection, useFirestore } from '@/firebase';
import type { Project } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { FolderKanban, Plus, ExternalLink, Trash2, Search, MapPin, Star, Pencil } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function AdminProjectsPage() {
  const firestore = useFirestore();
  const { data: projects, loading } = useCollection<Project>(firestore ? collection(firestore, 'projects') : null);
  const [search, setSearch] = useState('');
  const { toast } = useToast();

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase();
    return (projects ?? []).filter((project) => !term || [project.title, project.location, project.category, ...(project.tags ?? [])].filter(Boolean).join(' ').toLowerCase().includes(term));
  }, [projects, search]);

  const removeProject = async (project: Project) => {
    if (!firestore || !window.confirm(`Delete “${project.title}” from the portfolio?`)) return;
    try {
      await deleteDoc(doc(firestore, 'projects', project.id));
      toast({ title: 'Project deleted', description: `${project.title} has been removed.` });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Could not delete project.';
      toast({ variant: 'destructive', title: 'Delete failed', description: message });
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div><p className="eyebrow">Portfolio management</p><h1 className="mt-2 font-headline text-4xl font-bold tracking-tight">Projects</h1><p className="mt-2 max-w-2xl text-muted-foreground">Manage public case studies, featured projects and unpublished work from one place.</p></div>
        <Button asChild className="rounded-xl"><Link href="/admin/dashboard/add-project"><Plus className="mr-2 h-4 w-4" />Add project</Link></Button>
      </div>
      <div className="flex items-center gap-3 rounded-2xl border bg-secondary/30 p-4"><div className="relative max-w-xl flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by name, location or tag" className="rounded-xl pl-9 bg-background" /></div><span className="hidden text-sm text-muted-foreground sm:inline">{projects?.length ?? 0} total</span></div>
      {loading ? <div className="grid gap-5 lg:grid-cols-2">{[1,2,3,4].map(item => <Card key={item} className="overflow-hidden rounded-2xl"><div className="aspect-[16/9] animate-pulse bg-muted" /><div className="space-y-3 p-5"><div className="h-5 w-1/2 animate-pulse rounded bg-muted" /><div className="h-4 w-full animate-pulse rounded bg-muted" /></div></Card>)}</div> : filtered.length ? <div className="grid gap-5 lg:grid-cols-2">{filtered.map(project => <Card key={project.id} className="overflow-hidden rounded-2xl"><div className="relative aspect-[16/9] bg-muted">{project.imageUrl ? <Image src={project.imageUrl} alt={project.title} fill sizes="(min-width: 1024px) 45vw, 100vw" className="object-cover" /> : <div className="flex h-full items-center justify-center"><FolderKanban className="h-10 w-10 text-muted-foreground" /></div>}<div className="absolute left-4 top-4 flex flex-wrap gap-2"><Badge className="bg-black/65 text-white backdrop-blur">{project.category}</Badge>{project.status && <Badge className="bg-primary text-[#0d1724]">{project.status}</Badge>}{project.featured && <Badge className="bg-white text-[#0d1724]"><Star className="mr-1 h-3 w-3 fill-current" />Featured</Badge>}</div></div><CardContent className="p-5"><div className="flex items-start justify-between gap-4"><div><h2 className="font-headline text-xl font-bold">{project.title}</h2><p className="mt-1 flex items-center gap-1 text-sm text-muted-foreground"><MapPin className="h-3.5 w-3.5" />{project.location || 'Location not set'}</p></div><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${project.visible === false ? 'bg-muted text-muted-foreground' : 'bg-emerald-100 text-emerald-800'}`}>{project.visible === false ? 'Draft' : 'Published'}</span></div><p className="mt-4 line-clamp-2 text-sm leading-6 text-muted-foreground">{project.description}</p><div className="mt-5 flex flex-wrap gap-2">{(project.tags ?? []).slice(0, 4).map(tag => <span key={tag} className="rounded-full bg-secondary px-2.5 py-1 text-xs text-secondary-foreground">{tag}</span>)}</div><div className="mt-6 flex flex-wrap gap-2"><Button asChild variant="outline" className="rounded-xl"><Link href={`/admin/dashboard/projects/${project.id}/edit`}><Pencil className="mr-2 h-4 w-4" />Edit</Link></Button><Button asChild variant="outline" className="rounded-xl"><Link href={`/projects/${project.id}`} target="_blank"><ExternalLink className="mr-2 h-4 w-4" />Preview</Link></Button><Button variant="destructive" className="rounded-xl" onClick={() => removeProject(project)}><Trash2 className="mr-2 h-4 w-4" />Delete</Button></div></CardContent></Card>)}</div> : <Card className="rounded-2xl border-dashed"><CardContent className="px-6 py-20 text-center"><FolderKanban className="mx-auto h-10 w-10 text-primary" /><h2 className="mt-5 font-headline text-2xl font-bold">No projects yet</h2><p className="mx-auto mt-2 max-w-lg text-muted-foreground">Add your first real project with a cover image, gallery, scope and project facts.</p><Button asChild className="mt-6 rounded-xl"><Link href="/admin/dashboard/add-project"><Plus className="mr-2 h-4 w-4" />Add your first project</Link></Button></CardContent></Card>}
    </div>
  );
}

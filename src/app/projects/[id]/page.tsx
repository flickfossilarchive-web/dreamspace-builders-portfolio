import Image from 'next/image';
import Link from 'next/link';
import { ArrowLeft, ArrowRight, CheckCircle2, MapPin, Ruler, CalendarDays, Layers3 } from 'lucide-react';
import { doc, getDoc, getFirestore } from 'firebase/firestore';
import { initializeFirebase } from '@/firebase';
import type { Project } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { notFound } from 'next/navigation';

export const dynamic = 'force-dynamic';

async function getProject(id: string): Promise<Project | null> {
  try {
    const { firebaseApp } = initializeFirebase();
    const db = getFirestore(firebaseApp);
    const snapshot = await getDoc(doc(db, 'projects', id));
    if (!snapshot.exists()) return null;
    return { id: snapshot.id, ...(snapshot.data() as Omit<Project, 'id'>) };
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const project = await getProject(id);
  if (!project) return { title: 'Project not found' };
  return {
    title: project.title,
    description: project.description,
    openGraph: { images: project.imageUrl ? [project.imageUrl] : [] },
  };
}

export default async function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const project = await getProject(id);
  if (!project || project.visible === false) notFound();

  const gallery = [project.imageUrl, ...(project.galleryUrls ?? [])].filter(Boolean);
  const facts = [
    project.location && { label: 'Location', value: project.location, icon: MapPin },
    project.completionYear && { label: 'Year', value: String(project.completionYear), icon: CalendarDays },
    project.area && { label: 'Area', value: project.area, icon: Ruler },
    project.scope && { label: 'Scope', value: project.scope, icon: Layers3 },
  ].filter(Boolean) as Array<{ label: string; value: string; icon: typeof MapPin }>;

  return (
    <main className="bg-background">
      <section className="relative overflow-hidden bg-[#0b1522] text-white">
        <div className="absolute inset-0"><Image src={project.imageUrl} alt={project.title} fill priority sizes="100vw" className="object-cover" /></div>
        <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(4,10,17,0.9),rgba(4,10,17,0.55),rgba(4,10,17,0.2))]" />
        <div className="absolute inset-0 bg-[linear-gradient(0deg,rgba(4,10,17,0.92),transparent_65%)]" />
        <div className="section-shell relative z-10 flex min-h-[620px] items-end pb-16 pt-28 md:pb-24">
          <div className="max-w-4xl">
            <Link href="/projects" className="inline-flex items-center gap-2 text-sm text-white/65 hover:text-primary"><ArrowLeft className="h-4 w-4" /> Back to projects</Link>
            <div className="mt-7 flex flex-wrap gap-2"><Badge className="bg-primary text-[#0b1522]">{project.category}</Badge>{project.status && <Badge className="border-white/20 bg-white/10 text-white">{project.status}</Badge>}</div>
            <h1 className="mt-5 font-headline text-5xl font-bold leading-[1.02] tracking-[-0.035em] sm:text-6xl md:text-7xl">{project.title}</h1>
            <p className="mt-6 max-w-2xl text-base leading-8 text-white/72 sm:text-lg">{project.description}</p>
          </div>
        </div>
      </section>

      <section className="section-shell py-16 md:py-24">
        <div className="grid gap-10 lg:grid-cols-[1.2fr_0.8fr]">
          <div>
            <p className="eyebrow">Project overview</p>
            <h2 className="mt-4 font-headline text-3xl font-bold tracking-tight sm:text-4xl">The work behind the space.</h2>
            <div className="gold-line mt-5" />
            <p className="mt-7 whitespace-pre-line text-base leading-8 text-muted-foreground">{project.scope}</p>
            {(project.challenges || project.approach) && <div className="mt-10 grid gap-6 md:grid-cols-2">{project.challenges && <div className="rounded-2xl border bg-secondary/40 p-6"><p className="eyebrow">Challenge</p><p className="mt-3 text-sm leading-7 text-muted-foreground">{project.challenges}</p></div>}{project.approach && <div className="rounded-2xl border bg-secondary/40 p-6"><p className="eyebrow">Approach</p><p className="mt-3 text-sm leading-7 text-muted-foreground">{project.approach}</p></div>}</div>}
          </div>
          <div className="rounded-2xl border bg-card p-6 shadow-sm">
            <p className="eyebrow">Project facts</p>
            <div className="mt-5 divide-y">{facts.map(({ label, value, icon: Icon }) => <div key={label} className="flex gap-4 py-5 first:pt-0 last:pb-0"><Icon className="mt-0.5 h-5 w-5 shrink-0 text-primary" /><div><p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">{label}</p><p className="mt-1 text-sm font-semibold leading-6">{value}</p></div></div>)}</div>
            {project.tags?.length > 0 && <div className="mt-7 border-t pt-6"><p className="eyebrow">Tags</p><div className="mt-3 flex flex-wrap gap-2">{project.tags.map(tag => <span key={tag} className="rounded-full bg-secondary px-3 py-1 text-xs font-medium text-secondary-foreground">{tag}</span>)}</div></div>}
          </div>
        </div>
      </section>

      {project.highlights?.length ? <section className="bg-secondary py-16 md:py-24"><div className="section-shell"><p className="eyebrow">Highlights</p><h2 className="mt-4 font-headline text-3xl font-bold sm:text-4xl">What stands out.</h2><div className="mt-8 grid gap-4 md:grid-cols-2">{project.highlights.map(item => <div key={item} className="flex gap-3 rounded-2xl border bg-background p-5"><CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-primary" /><p className="text-sm leading-7 text-muted-foreground">{item}</p></div>)}</div></div></section> : null}

      {gallery.length > 0 && <section className="section-shell py-16 md:py-24"><div className="flex items-end justify-between gap-6"><div><p className="eyebrow">Gallery</p><h2 className="mt-4 font-headline text-3xl font-bold sm:text-4xl">See the project.</h2></div><span className="text-sm text-muted-foreground">{gallery.length} {gallery.length === 1 ? 'image' : 'images'}</span></div><div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{gallery.map((url, index) => <div key={`${url}-${index}`} className="relative aspect-[4/3] overflow-hidden rounded-2xl bg-muted"><Image src={url} alt={`${project.title} — image ${index + 1}`} fill sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw" className="object-cover transition-transform duration-700 hover:scale-[1.03]" /></div>)}</div></section>}

      <section className="section-shell pb-20 md:pb-28"><div className="overflow-hidden rounded-3xl bg-[#0d1724] p-8 text-white sm:p-12 md:p-16"><p className="eyebrow text-primary">Build something similar</p><h2 className="mt-4 max-w-2xl font-headline text-4xl font-bold sm:text-5xl">Have a project with a similar ambition?</h2><p className="mt-5 max-w-2xl text-base leading-7 text-white/65">Tell us about your site, scope and what you want to achieve. We’ll help you work out the next step.</p><Button asChild size="lg" className="mt-8 rounded-xl bg-primary px-7 text-[#0d1724] hover:bg-primary/90"><Link href="/contact">Start a project <ArrowRight className="ml-2 h-4 w-4" /></Link></Button></div></section>
    </main>
  );
}

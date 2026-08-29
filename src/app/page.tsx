'use client';

import Link from 'next/link';
import { useMemo } from 'react';
import { ArrowRight, Building, Palette, Users, PenTool, GanttChartSquare, DraftingCompass, Rss, Layers, Mail, Calculator, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ProjectCard } from '@/components/project-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import placeholderImages from '@/lib/placeholder-images.json';
import Image from 'next/image';
import { useCollection, useFirestore } from '@/firebase';
import type { Project } from '@/lib/types';
import { collection, query, where } from 'firebase/firestore';

const services = [
  { icon: Building, title: 'Building Construction', description: 'High-quality construction for residential, commercial, and industrial projects.' },
  { icon: GanttChartSquare, title: 'Contracting', description: 'Comprehensive contracting services, managing the project from planning through delivery.' },
  { icon: Users, title: 'Consulting', description: 'Practical guidance to help you make confident decisions at every project stage.' },
  { icon: DraftingCompass, title: 'Drafting', description: 'Precision drafting and cost estimation to support clear and effective planning.' },
  { icon: Rss, title: 'Supervision', description: 'Dedicated site supervision focused on quality, coordination, and specifications.' },
  { icon: Palette, title: 'Interior Designing', description: 'Creative and functional interior solutions tailored to your vision and space.' },
  { icon: PenTool, title: 'Architect Engineer', description: 'Architectural and engineering support to turn concepts into buildable plans.' },
  { icon: Layers, title: 'Turnkey Projects', description: 'End-to-end solutions that bring planning, execution, and finishing together.' },
  { icon: Calculator, title: 'Estimation', description: 'Detailed cost estimation to help you plan your project budget with confidence.' },
];

const process = [
  ['1', 'Tell us your requirement', 'Share your project type, location, scope, and goals.'],
  ['2', 'Plan and estimate', 'We help shape the approach, drawings, scope, and estimated cost.'],
  ['3', 'Build with supervision', 'Execution is coordinated with attention to quality and specifications.'],
  ['4', 'Complete the project', 'We work toward a clear, organized handover of the finished space.'],
];

export default function Home() {
  const { hero } = placeholderImages;
  const firestore = useFirestore();
  const projectsQuery = useMemo(() => {
    if (!firestore) return null;
    return query(collection(firestore, 'projects'), where('featured', '==', true));
  }, [firestore]);

  const { data: featuredProjects, loading } = useCollection<Project>(projectsQuery);

  return (
    <div className="flex flex-col">
      <section className="relative min-h-[680px] h-[88vh] flex items-center text-white overflow-hidden">
        <div className="absolute inset-0 bg-black/55 z-10" />
        <Image src={hero.src} alt={hero.alt} fill className="object-cover" priority data-ai-hint={hero.hint} />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent z-20" />
        <div className="container mx-auto px-4 z-30 mt-auto mb-16 md:mb-24">
          <div className="max-w-4xl">
            <p className="mb-4 text-sm md:text-base font-semibold uppercase tracking-[0.22em] text-white/80">Construction & Design • Davanagere, Karnataka</p>
            <h1 className="font-headline text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight text-white drop-shadow-2xl">Dreamspace Builders</h1>
            <p className="mt-6 text-lg md:text-xl max-w-2xl text-neutral-200 leading-relaxed">
              From planning and estimation to construction, supervision and interiors, we help turn your ideas into well-executed spaces.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
              <Button asChild size="lg" className="font-semibold shadow-lg group text-base md:text-lg px-8 py-6 bg-primary text-primary-foreground hover:bg-primary/90">
                <Link href="/contact">Request a Quote <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" /></Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="font-semibold text-base md:text-lg px-8 py-6 bg-transparent text-white border-white/80 hover:bg-white hover:text-primary">
                <Link href="/projects">Explore Our Work</Link>
              </Button>
            </div>
            <div className="mt-8 flex flex-wrap gap-x-6 gap-y-2 text-sm text-white/80">
              <span className="inline-flex items-center gap-2"><CheckCircle2 className="h-4 w-4" /> Residential</span>
              <span className="inline-flex items-center gap-2"><CheckCircle2 className="h-4 w-4" /> Commercial</span>
              <span className="inline-flex items-center gap-2"><CheckCircle2 className="h-4 w-4" /> Industrial</span>
              <span className="inline-flex items-center gap-2"><CheckCircle2 className="h-4 w-4" /> Turnkey</span>
            </div>
          </div>
        </div>
      </section>

      <section id="services" className="py-20 md:py-28 bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16 max-w-3xl mx-auto">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">What we do</p>
            <h2 className="mt-3 text-4xl md:text-5xl font-headline font-bold tracking-tight text-foreground">One team for the full project</h2>
            <p className="mt-5 text-lg text-muted-foreground">A practical mix of construction, design, planning, estimation, engineering, and supervision services under one roof.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {services.map((service) => (
              <Card key={service.title} className="text-center bg-card shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group">
                <CardHeader className="items-center">
                  <div className="p-4 bg-primary/10 rounded-full w-fit group-hover:bg-primary transition-colors duration-300">
                    <service.icon className="h-10 w-10 text-primary group-hover:text-primary-foreground transition-colors duration-300" />
                  </div>
                  <CardTitle className="font-headline mt-4 text-xl">{service.title}</CardTitle>
                </CardHeader>
                <CardContent><p className="text-muted-foreground text-sm leading-6">{service.description}</p></CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 md:py-28 bg-secondary">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center mb-14">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">A simple process</p>
            <h2 className="mt-3 text-4xl md:text-5xl font-headline font-bold tracking-tight">From idea to finished space</h2>
            <p className="mt-5 text-lg text-muted-foreground">A clear path helps you understand what happens next and keeps your project moving.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {process.map(([number, title, description]) => (
              <Card key={number} className="border bg-background/70 shadow-sm">
                <CardContent className="p-7">
                  <div className="h-10 w-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">{number}</div>
                  <h3 className="mt-5 font-headline text-xl font-semibold">{title}</h3>
                  <p className="mt-3 text-sm leading-6 text-muted-foreground">{description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="mt-12 text-center">
            <Button asChild size="lg"><Link href="/contact">Discuss Your Project <ArrowRight className="ml-2 h-5 w-5" /></Link></Button>
          </div>
        </div>
      </section>

      <section className="py-20 md:py-28 bg-background">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-12">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">Portfolio</p>
              <h2 className="mt-3 text-4xl md:text-5xl font-headline font-bold tracking-tight">Featured Projects</h2>
              <p className="mt-4 text-lg text-muted-foreground max-w-2xl">A glimpse into our work. View the full portfolio for projects by category.</p>
            </div>
            <Button asChild variant="outline"><Link href="/projects">View All Projects <ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
          </div>
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {[1, 2, 3].map((item) => (
                <Card key={item}><CardHeader className="p-0"><div className="relative aspect-video w-full overflow-hidden bg-muted animate-pulse" /></CardHeader><CardContent className="space-y-3 p-6"><div className="h-6 w-3/4 bg-muted animate-pulse rounded-md" /><div className="h-4 w-full bg-muted animate-pulse rounded-md" /></CardContent></Card>
              ))}
            </div>
          ) : featuredProjects && featuredProjects.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {featuredProjects.map((project) => <ProjectCard key={project.id} project={project} />)}
            </div>
          ) : (
            <Card className="border-dashed">
              <CardContent className="py-16 text-center">
                <h3 className="text-2xl font-semibold">Our portfolio is being updated</h3>
                <p className="mt-3 max-w-xl mx-auto text-muted-foreground">Contact us to discuss your project or ask about our recent work.</p>
                <Button asChild className="mt-7"><Link href="/contact">Talk to Dreamspace Builders <ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
              </CardContent>
            </Card>
          )}
        </div>
      </section>

      <section className="py-20 md:py-24 bg-primary text-primary-foreground">
        <div className="container mx-auto px-4 text-center">
          <Mail className="mx-auto h-10 w-10 mb-5 opacity-90" />
          <h2 className="text-4xl md:text-5xl font-headline font-bold">Have a project in mind?</h2>
          <p className="mt-5 text-lg md:text-xl max-w-2xl mx-auto opacity-90">Tell us what you are planning. We’ll help you work through the next steps.</p>
          <Button asChild size="lg" variant="secondary" className="mt-8 font-semibold"><Link href="/contact">Request a Quote <ArrowRight className="ml-2 h-5 w-5" /></Link></Button>
        </div>
      </section>
    </div>
  );
}

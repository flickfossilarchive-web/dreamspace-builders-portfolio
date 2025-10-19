'use client';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ProjectCard } from '@/components/project-card';
import { ArrowRight, Building, Palette, Users, PenTool, GanttChartSquare, DraftingCompass, Rss, Layers, Mail } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import placeholderImages from '@/lib/placeholder-images.json';
import Image from 'next/image';
import { useCollection, useFirestore } from '@/firebase';
import type { Project } from '@/lib/types';
import { collection, query, where } from 'firebase/firestore';
import { useMemo } from 'react';

const services = [
    {
        icon: Building,
        title: "Building Construction",
        description: "High-quality construction for residential, commercial, and industrial projects."
    },
    {
        icon: GanttChartSquare,
        title: "Contracting",
        description: "Comprehensive contracting services, managing all aspects of your project."
    },
    {
        icon: Users,
        title: "Consulting",
        description: "Expert consulting to guide you through every phase of your project."
    },
    {
        icon: DraftingCompass,
        title: "Drafting & Estimation",
        description: "Precision drafting and accurate cost estimation for effective planning."
    },
    {
        icon: Rss,
        title: "Supervision",
        description: "Dedicated on-site supervision to ensure quality control and adherence to specs."
    },
    {
        icon: Palette,
        title: "Interior Designing",
        description: "Creative and functional interior design solutions that bring your vision to life."
    },
    {
        icon: PenTool,
        title: "Architect Engineer",
        description: "Innovative architectural and engineering services to design your structure."
    },
    {
        icon: Layers,
        title: "Turn Key Projects",
        description: "Complete turn-key solutions, from concept to completion."
    },
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
      {/* Hero Section */}
      <section className="relative h-[90vh] min-h-[600px] flex items-center text-white overflow-hidden">
        <Image
          src={hero.src}
          alt={hero.alt}
          fill
          className="object-cover"
          priority
          data-ai-hint={hero.hint}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-transparent z-10"></div>
        <div className="container mx-auto px-4 z-20 mt-auto mb-20 md:mb-32">
          <div className="max-w-4xl">
            <h1 className="font-headline text-5xl md:text-7xl lg:text-8xl font-extrabold tracking-tight text-white">
              DreamSpace Builders
            </h1>
            <p className="mt-6 text-lg md:text-xl max-w-2xl text-neutral-300">
              BUILT By YOU..... We deliver excellence in construction and design, creating spaces that inspire.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row items-start gap-4">
              <Button asChild size="lg" className="font-semibold shadow-lg group text-lg px-8 py-6 bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-300 transform hover:scale-105">
                <Link href="/projects">
                  Explore Our Work
                  <ArrowRight className="ml-2 h-5 w-5 transition-transform duration-300 group-hover:translate-x-1" />
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="font-semibold text-lg px-8 py-6 text-white hover:bg-white/10 transition-all duration-300 transform hover:scale-105 border-white/50">
                <Link href="/contact">
                  Request a Quote
                  <Mail className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-20 md:py-28 bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16 max-w-3xl mx-auto">
            <h2 className="text-4xl md:text-5xl font-headline font-bold tracking-tight text-primary">Our Expertise</h2>
            <p className="mt-4 text-lg text-muted-foreground">
              We offer a comprehensive suite of services to bring your vision to life with quality, integrity, and innovation at every step.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {services.map((service, index) => (
              <Card key={index} className="text-center bg-card/50 backdrop-blur-sm border border-border/50 shadow-lg hover:shadow-primary/20 hover:-translate-y-2 transition-all duration-300 group">
                <CardHeader className="items-center">
                  <div className="p-4 bg-primary/10 rounded-full w-fit group-hover:bg-primary transition-colors duration-300">
                    <service.icon className="h-10 w-10 text-primary group-hover:text-primary-foreground transition-colors duration-300" />
                  </div>
                  <CardTitle className="font-headline mt-4 text-xl">{service.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground text-sm">
                    {service.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Projects Section */}
      <section className="py-20 md:py-28 bg-secondary">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-headline font-bold tracking-tight text-primary">Featured Projects</h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              A glimpse into our finest work and commitment to excellence.
            </p>
          </div>
          {loading ? (
             <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <Card><CardHeader className="p-0"><div className="relative aspect-video w-full overflow-hidden bg-muted animate-pulse"></div></CardHeader><CardContent className="space-y-2 mt-6 p-6"><div className="h-6 w-3/4 bg-muted animate-pulse rounded-md"></div><div className="h-4 w-full bg-muted animate-pulse rounded-md"></div></CardContent><CardFooter className="p-6"><div className="h-10 w-full bg-muted animate-pulse rounded-md"></div></CardFooter></Card>
                <Card><CardHeader className="p-0"><div className="relative aspect-video w-full overflow-hidden bg-muted animate-pulse"></div></CardHeader><CardContent className="space-y-2 mt-6 p-6"><div className="h-6 w-3/4 bg-muted animate-pulse rounded-md"></div><div className="h-4 w-full bg-muted animate-pulse rounded-md"></div></CardContent><CardFooter className="p-6"><div className="h-10 w-full bg-muted animate-pulse rounded-md"></div></CardFooter></Card>
                <Card><CardHeader className="p-0"><div className="relative aspect-video w-full overflow-hidden bg-muted animate-pulse"></div></CardHeader><CardContent className="space-y-2 mt-6 p-6"><div className="h-6 w-3/4 bg-muted animate-pulse rounded-md"></div><div className="h-4 w-full bg-muted animate-pulse rounded-md"></div></CardContent><CardFooter className="p-6"><div className="h-10 w-full bg-muted animate-pulse rounded-md"></div></CardFooter></Card>
             </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {featuredProjects?.map((project) => (
                <ProjectCard key={project.id} project={project} />
                ))}
            </div>
          )}
           <div className="text-center mt-16">
            <Button asChild size="lg" variant="outline">
              <Link href="/projects">
                View All Projects <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}

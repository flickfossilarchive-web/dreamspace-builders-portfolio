import Image from 'next/image';
import Link from 'next/link';
import { Building, Users, Target, BarChart2, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import placeholderImages from '@/lib/placeholder-images.json';

export default function AboutPage() {
  const { about } = placeholderImages;
  return (
    <div className="container mx-auto px-4 py-16 md:py-24">
      <div className="text-center mb-16 max-w-3xl mx-auto">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">About us</p>
        <h1 className="mt-3 text-5xl md:text-6xl font-bold font-headline text-foreground">Dreamspace Builders</h1>
        <p className="mt-5 text-lg text-muted-foreground">Construction and design services focused on turning clear requirements into thoughtfully planned, well-executed spaces.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-12 items-center">
        <div className="lg:col-span-2">
          <Image src={about.src} alt={about.alt} width={about.width} height={about.height} className="rounded-lg shadow-lg object-cover" data-ai-hint={about.hint} />
        </div>
        <div className="lg:col-span-3 space-y-8">
          <div>
            <h2 className="text-3xl font-headline font-bold text-foreground mb-4">Who We Are</h2>
            <p className="text-muted-foreground text-lg leading-relaxed">
              Dreamspace Builders is based in Davanagere, Karnataka, and provides construction and design support across residential, commercial, and industrial projects. Our services cover building construction, contracting, consulting, drafting, estimation, supervision, architectural and engineering support, interiors, and turnkey projects.
            </p>
          </div>
          <div>
            <h2 className="text-3xl font-headline font-bold text-foreground mb-4">How We Work</h2>
            <p className="text-muted-foreground text-lg leading-relaxed">
              We start by understanding the requirement, then help structure the scope, planning, drawings and estimate before moving into execution and supervision. The goal is simple: keep communication clear, decisions practical, and the work aligned with the agreed requirement.
            </p>
          </div>
          <Button asChild size="lg" className="font-semibold"><Link href="/contact">Discuss Your Project <ArrowRight className="ml-2 h-5 w-5" /></Link></Button>
        </div>
      </div>

      <div className="py-20 md:py-28">
        <div className="text-center mb-16">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">Our values</p>
          <h2 className="mt-3 text-4xl font-headline font-bold tracking-tight text-foreground">What guides our work</h2>
          <p className="mt-3 text-lg text-muted-foreground max-w-2xl mx-auto">The principles we want clients to experience throughout the project.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {[
            [Building, 'Quality', 'Focus on dependable workmanship, materials, and attention to detail.'],
            [Users, 'Integrity', 'Keep communication honest, expectations clear, and decisions transparent.'],
            [Target, 'Practical Innovation', 'Use thoughtful ideas and suitable technology where they add real value.'],
            [BarChart2, 'Client-Centric', 'Keep the project aligned with the client’s requirements, priorities, and goals.'],
          ].map(([Icon, title, description]) => {
            const ValueIcon = Icon as typeof Building;
            return (
              <Card key={String(title)} className="text-center bg-card shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
                <CardHeader>
                  <div className="mx-auto bg-primary/10 rounded-full p-4 w-fit"><ValueIcon className="h-10 w-10 text-primary" /></div>
                  <CardTitle className="font-headline mt-4 text-2xl">{String(title)}</CardTitle>
                </CardHeader>
                <CardContent><p className="text-muted-foreground leading-6">{String(description)}</p></CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ProjectCard } from '@/components/project-card';
import { projects } from '@/lib/data';
import { ArrowRight, Building, Palette, Users } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function Home() {
  const featuredProjects = projects.filter((p) => p.featured);

  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative py-24 md:py-32 bg-primary/10">
        <div className="container mx-auto text-center px-4">
          <h1 className="font-headline text-4xl md:text-6xl font-bold tracking-tight text-primary-foreground drop-shadow-md bg-primary p-4 rounded-lg inline-block">
            DreamSpace Builders
          </h1>
          <p className="mt-6 text-lg md:text-xl max-w-3xl mx-auto text-foreground/80">
            Building the future, together. We deliver excellence in construction and design.
          </p>
          <div className="mt-8 flex justify-center gap-4">
            <Button asChild size="lg" className="bg-accent hover:bg-accent/90 text-accent-foreground">
              <Link href="/projects">
                View Our Work <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/contact">Get a Quote</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Why Choose Us Section */}
      <section className="py-16 md:py-24 bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-headline font-bold tracking-tight text-primary">Our Services</h2>
            <p className="mt-2 text-lg text-muted-foreground">
              Experience, innovation, and commitment.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="text-center shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader>
                <div className="mx-auto bg-primary/10 rounded-full p-4 w-fit">
                  <Building className="h-8 w-8 text-primary" />
                </div>
                <CardTitle className="font-headline mt-4">Building Construction</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Our commitment to quality is unwavering. We use the best materials and skilled labor to ensure every project is built to last.
                </p>
              </CardContent>
            </Card>
            <Card className="text-center shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader>
                <div className="mx-auto bg-primary/10 rounded-full p-4 w-fit">
                  <Palette className="h-8 w-8 text-primary" />
                </div>
                <CardTitle className="font-headline mt-4">Interior Designing</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  From concept to completion, our team creates beautiful and functional spaces tailored to your lifestyle and vision.
                </p>
              </CardContent>
            </Card>
            <Card className="text-center shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader>
                <div className="mx-auto bg-primary/10 rounded-full p-4 w-fit">
                  <Users className="h-8 w-8 text-primary" />
                </div>
                <CardTitle className="font-headline mt-4">Expert Consultation</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                 Our team of architects and engineers provide expert guidance and supervision for all your project needs.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Featured Projects Section */}
      <section className="py-16 md:py-24 bg-secondary">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-headline font-bold tracking-tight text-primary">Featured Projects</h2>
            <p className="mt-2 text-lg text-muted-foreground">
              A glimpse into our finest work.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredProjects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
           <div className="text-center mt-12">
            <Button asChild size="lg" variant="outline">
              <Link href="/projects">
                See All Projects <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}

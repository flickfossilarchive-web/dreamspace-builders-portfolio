import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ProjectCard } from '@/components/project-card';
import { projects } from '@/lib/data';
import { ArrowRight, Building, Palette, Users, Star } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function Home() {
  const featuredProjects = projects.filter((p) => p.featured);

  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative min-h-[60vh] md:min-h-[80vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/50 to-transparent z-10"></div>
        <div className="absolute inset-0 bg-gradient-to-b from-primary/10 to-transparent"></div>
        <div className="container mx-auto text-center px-4 z-20">
          <h1 className="font-headline text-5xl md:text-7xl font-extrabold tracking-tight text-foreground drop-shadow-lg">
            DreamSpace Builders
          </h1>
          <p className="mt-6 text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground">
            BUILT By YOU..... We deliver excellence in construction and design, creating spaces that inspire.
          </p>
          <div className="mt-10 flex justify-center gap-4">
            <Button asChild size="lg" className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold shadow-lg">
              <Link href="/projects">
                Explore Our Work <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="font-semibold shadow-lg">
              <Link href="/contact">Request a Quote</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section className="py-20 md:py-28 bg-secondary">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-headline font-bold tracking-tight text-primary">Our Core Services</h2>
            <p className="mt-3 text-lg text-muted-foreground max-w-2xl mx-auto">
              From initial concept to final execution, we provide comprehensive solutions with a focus on quality and innovation.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="text-center bg-card/50 backdrop-blur-sm border border-border/50 shadow-lg hover:shadow-primary/20 hover:-translate-y-2 transition-all duration-300">
              <CardHeader>
                <div className="mx-auto bg-primary/10 rounded-full p-4 w-fit">
                  <Building className="h-10 w-10 text-primary" />
                </div>
                <CardTitle className="font-headline mt-4 text-2xl">Building Construction</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Our commitment to quality is unwavering. We use the best materials and skilled labor to ensure every project is built to last.
                </p>
              </CardContent>
            </Card>
            <Card className="text-center bg-card/50 backdrop-blur-sm border border-border/50 shadow-lg hover:shadow-primary/20 hover:-translate-y-2 transition-all duration-300">
              <CardHeader>
                <div className="mx-auto bg-primary/10 rounded-full p-4 w-fit">
                  <Palette className="h-10 w-10 text-primary" />
                </div>
                <CardTitle className="font-headline mt-4 text-2xl">Interior Designing</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  From concept to completion, our team creates beautiful and functional spaces tailored to your lifestyle and vision.
                </p>
              </CardContent>
            </Card>
            <Card className="text-center bg-card/50 backdrop-blur-sm border border-border/50 shadow-lg hover:shadow-primary/20 hover:-translate-y-2 transition-all duration-300">
              <CardHeader>
                <div className="mx-auto bg-primary/10 rounded-full p-4 w-fit">
                  <Users className="h-10 w-10 text-primary" />
                </div>
                <CardTitle className="font-headline mt-4 text-2xl">Expert Consultation</CardTitle>
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
      <section className="py-20 md:py-28 bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-headline font-bold tracking-tight text-primary">Featured Projects</h2>
            <p className="mt-3 text-lg text-muted-foreground max-w-2xl mx-auto">
              A glimpse into our finest work and commitment to excellence.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredProjects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
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

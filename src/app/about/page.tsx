import Image from 'next/image';
import { Building, Users, Target, BarChart2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import placeholderImages from '@/lib/placeholder-images.json';

export default function AboutPage() {
  const { about } = placeholderImages;
  return (
    <div className="container mx-auto px-4 py-16 md:py-24">
      <div className="text-center mb-16">
        <h1 className="text-5xl md:text-6xl font-bold font-headline text-primary">About DreamSpace Builders</h1>
        <p className="mt-4 text-lg text-muted-foreground max-w-3xl mx-auto">
          Pioneering the future of construction with integrity, innovation, and unparalleled quality.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-12 items-center">
        <div className="lg:col-span-2">
          <Image 
            src={about.src}
            alt={about.alt}
            width={about.width}
            height={about.height}
            className="rounded-lg shadow-lg object-cover"
            data-ai-hint={about.hint}
          />
        </div>
        <div className="lg:col-span-3 space-y-8">
          <div>
            <h2 className="text-3xl font-headline font-bold text-primary mb-4">Who We Are</h2>
            <p className="text-muted-foreground text-lg leading-relaxed">
              DreamSpace Builders is a premier construction and design firm dedicated to turning visions into reality. With years of experience in residential, commercial, and industrial projects, we have built a reputation for excellence, reliability, and innovation. Our team is our greatest asset—a collective of skilled architects, engineers, designers, and builders passionate about crafting spaces that are not only aesthetically pleasing but also functional and enduring. We believe in a collaborative approach, working closely with our clients from the initial concept to the final nail, ensuring every detail reflects their dreams.
            </p>
          </div>
           <div>
            <h2 className="text-3xl font-headline font-bold text-primary mb-4">Our Philosophy</h2>
            <p className="text-muted-foreground text-lg leading-relaxed">
              Our philosophy is simple: Build with purpose. We are committed to sustainable practices, utilizing eco-friendly materials and energy-efficient designs to minimize our environmental impact. Quality is at the core of everything we do; we don't just build structures, we build lasting relationships and communities. For us, every project is a partnership and an opportunity to create something extraordinary.
            </p>
          </div>
        </div>
      </div>

       <div className="py-20 md:py-28">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-headline font-bold tracking-tight text-primary">Our Core Values</h2>
          <p className="mt-3 text-lg text-muted-foreground max-w-2xl mx-auto">
            The principles that guide our work and define our character.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <Card className="text-center bg-card/50 backdrop-blur-sm border border-border/50 shadow-lg hover:shadow-primary/20 hover:-translate-y-2 transition-all duration-300">
            <CardHeader>
              <div className="mx-auto bg-primary/10 rounded-full p-4 w-fit">
                <Building className="h-10 w-10 text-primary" />
              </div>
              <CardTitle className="font-headline mt-4 text-2xl">Quality</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                We are committed to the highest standards of craftsmanship and materials.
              </p>
            </CardContent>
          </Card>
          <Card className="text-center bg-card/50 backdrop-blur-sm border border-border/50 shadow-lg hover:shadow-primary/20 hover:-translate-y-2 transition-all duration-300">
            <CardHeader>
              <div className="mx-auto bg-primary/10 rounded-full p-4 w-fit">
                <Users className="h-10 w-10 text-primary" />
              </div>
              <CardTitle className="font-headline mt-4 text-2xl">Integrity</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                We build relationships based on trust, honesty, and transparency.
              </p>
            </CardContent>
          </Card>
          <Card className="text-center bg-card/50 backdrop-blur-sm border border-border/50 shadow-lg hover:shadow-primary/20 hover:-translate-y-2 transition-all duration-300">
            <CardHeader>
              <div className="mx-auto bg-primary/10 rounded-full p-4 w-fit">
                <Target className="h-10 w-10 text-primary" />
              </div>
              <CardTitle className="font-headline mt-4 text-2xl">Innovation</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                We embrace new technologies and creative solutions to deliver superior results.
              </p>
            </CardContent>
          </Card>
          <Card className="text-center bg-card/50 backdrop-blur-sm border border-border/50 shadow-lg hover:shadow-primary/20 hover:-translate-y-2 transition-all duration-300">
            <CardHeader>
              <div className="mx-auto bg-primary/10 rounded-full p-4 w-fit">
                <BarChart2 className="h-10 w-10 text-primary" />
              </div>
              <CardTitle className="font-headline mt-4 text-2xl">Client-Centric</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Our clients' satisfaction is the measure of our success.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

    </div>
  );
}

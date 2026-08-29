import { ContactForm } from '@/components/contact-form';
import { Mail, Phone, MapPin, MessageCircle, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

const address = '#70/7, 15th Cross Road, Nijalingappa Layout, Davanagere - 577004';
const email = 'Dreamspacebuilders12@gmail.com';
const phone = '+91 9008592532';
const mapsUrl = 'https://www.google.com/maps/search/?api=1&query=%2370%2F7%2C%2015th%20Cross%20Road%2C%20Nijalingappa%20Layout%2C%20Davanagere%20577004';
const whatsappUrl = 'https://wa.me/919008592532';

export default function ContactPage() {
  return (
    <div className="container mx-auto px-4 py-16 md:py-24">
      <div className="text-center mb-14 max-w-3xl mx-auto">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">Start a conversation</p>
        <h1 className="mt-3 text-5xl md:text-6xl font-bold font-headline text-foreground">Let’s discuss your project</h1>
        <p className="mt-5 text-lg text-muted-foreground">
          Tell us what you are planning and we’ll help you understand the next steps, services, and information needed to move forward.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1.05fr_0.95fr] gap-10 max-w-6xl mx-auto">
        <div className="bg-card p-7 md:p-9 rounded-2xl shadow-lg border">
          <div className="mb-7">
            <h2 className="text-3xl font-headline text-foreground">Send a Project Enquiry</h2>
            <p className="mt-2 text-sm text-muted-foreground">Including the project location and approximate scope helps us understand your requirement faster.</p>
          </div>
          <ContactForm />
        </div>

        <div className="space-y-6">
          <div className="rounded-2xl border bg-secondary/60 p-7">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">Direct contact</p>
            <div className="mt-6 space-y-5">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 h-12 w-12 flex items-center justify-center rounded-full bg-primary/10"><MapPin className="h-6 w-6 text-primary" /></div>
                <div><h3 className="font-semibold font-headline">Our Office</h3><p className="mt-1 text-sm text-muted-foreground leading-6">{address}</p><Button asChild variant="link" className="h-auto px-0 mt-1"><a href={mapsUrl} target="_blank" rel="noreferrer">Get directions <ArrowRight className="ml-1 h-4 w-4" /></a></Button></div>
              </div>
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 h-12 w-12 flex items-center justify-center rounded-full bg-primary/10"><Mail className="h-6 w-6 text-primary" /></div>
                <div><h3 className="font-semibold font-headline">Email</h3><a href={`mailto:${email}`} className="mt-1 block text-sm text-muted-foreground hover:text-primary transition-colors break-all">{email}</a></div>
              </div>
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 h-12 w-12 flex items-center justify-center rounded-full bg-primary/10"><Phone className="h-6 w-6 text-primary" /></div>
                <div><h3 className="font-semibold font-headline">Phone</h3><a href={`tel:${phone.replace(/\s/g, '')}`} className="mt-1 block text-sm text-muted-foreground hover:text-primary transition-colors">{phone}</a></div>
              </div>
            </div>
            <Button asChild className="mt-7 w-full font-semibold"><a href={whatsappUrl} target="_blank" rel="noreferrer"><MessageCircle className="mr-2 h-4 w-4" /> Chat on WhatsApp</a></Button>
          </div>

          <div className="rounded-2xl border p-7">
            <h2 className="text-2xl font-headline font-semibold">What to include</h2>
            <div className="mt-5 grid gap-3 text-sm text-muted-foreground">
              <p>• Project type: new build, renovation, commercial, industrial, or interior work.</p>
              <p>• Project location and approximate size.</p>
              <p>• The stage you are at: idea, drawings, estimation, or ready for execution.</p>
              <p>• Any specific service you need from our team.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

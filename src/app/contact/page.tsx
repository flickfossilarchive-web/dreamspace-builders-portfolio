import { ContactForm } from '@/components/contact-form';
import { Mail, Phone, MapPin } from 'lucide-react';

export default function ContactPage() {
  return (
    <div className="container mx-auto px-4 py-16 md:py-24">
      <div className="text-center mb-16">
        <h1 className="text-5xl md:text-6xl font-bold font-headline text-foreground">Get in Touch</h1>
        <p className="mt-4 text-lg text-muted-foreground max-w-3xl mx-auto">
          Have a project in mind, a question, or just want to say hello? We'd love to hear from you.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-12 max-w-6xl mx-auto">
        <div className="bg-card p-8 rounded-lg shadow-lg border">
          <h2 className="text-3xl font-headline text-foreground mb-6">Send Us a Message</h2>
          <ContactForm />
        </div>
        <div className="space-y-8 flex flex-col justify-center">
            <div className="flex items-start group">
                <div className="flex-shrink-0 h-14 w-14 flex items-center justify-center rounded-full bg-primary/10 group-hover:bg-primary transition-colors duration-300">
                    <MapPin className="h-7 w-7 text-primary group-hover:text-primary-foreground transition-colors duration-300" />
                </div>
                <div className="ml-4">
                    <h3 className="text-xl font-semibold font-headline">Our Office</h3>
                    <p className="text-muted-foreground">#70/7, 15th Cross Road, Nijalingappa Layout, Davanagere - 577004</p>
                </div>
            </div>
            <div className="flex items-start group">
                 <div className="flex-shrink-0 h-14 w-14 flex items-center justify-center rounded-full bg-primary/10 group-hover:bg-primary transition-colors duration-300">
                    <Mail className="h-7 w-7 text-primary group-hover:text-primary-foreground transition-colors duration-300" />
                </div>
                <div className="ml-4">
                    <h3 className="text-xl font-semibold font-headline">Email Us</h3>
                    <a href="mailto:Dreamspacebuilders12@gmail.com" className="text-muted-foreground hover:text-primary transition-colors">Dreamspacebuilders12@gmail.com</a>
                </div>
            </div>
             <div className="flex items-start group">
                 <div className="flex-shrink-0 h-14 w-14 flex items-center justify-center rounded-full bg-primary/10 group-hover:bg-primary transition-colors duration-300">
                    <Phone className="h-7 w-7 text-primary group-hover:text-primary-foreground transition-colors duration-300" />
                </div>
                <div className="ml-4">
                    <h3 className="text-xl font-semibold font-headline">Call Us</h3>
                    <a href="tel:+919008592532" className="text-muted-foreground hover:text-primary transition-colors">+91 9008592532</a>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}

import { ContactForm } from '@/components/contact-form';
import { Mail, Phone, MapPin } from 'lucide-react';

export default function ContactPage() {
  return (
    <div className="container mx-auto px-4 py-16 md:py-24">
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold font-headline text-primary">Get in Touch</h1>
        <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
          Have a project in mind or a question for us? We'd love to hear from you.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
        <div className="bg-card p-8 rounded-lg shadow-md">
          <h2 className="text-2xl font-headline text-primary mb-6">Contact Us</h2>
          <ContactForm />
        </div>
        <div className="space-y-8">
            <div className="flex items-start">
                <div className="flex-shrink-0 h-12 w-12 flex items-center justify-center rounded-full bg-primary/10">
                    <MapPin className="h-6 w-6 text-primary" />
                </div>
                <div className="ml-4">
                    <h3 className="text-lg font-semibold font-headline">Our Office</h3>
                    <p className="text-muted-foreground">123 Construction Ave, Buildtown, ST 12345</p>
                </div>
            </div>
            <div className="flex items-start">
                 <div className="flex-shrink-0 h-12 w-12 flex items-center justify-center rounded-full bg-primary/10">
                    <Mail className="h-6 w-6 text-primary" />
                </div>
                <div className="ml-4">
                    <h3 className="text-lg font-semibold font-headline">Email Us</h3>
                    <a href="mailto:contact@constructconnect.com" className="text-muted-foreground hover:text-primary transition-colors">contact@constructconnect.com</a>
                </div>
            </div>
             <div className="flex items-start">
                 <div className="flex-shrink-0 h-12 w-12 flex items-center justify-center rounded-full bg-primary/10">
                    <Phone className="h-6 w-6 text-primary" />
                </div>
                <div className="ml-4">
                    <h3 className="text-lg font-semibold font-headline">Call Us</h3>
                    <a href="tel:+1234567890" className="text-muted-foreground hover:text-primary transition-colors">(123) 456-7890</a>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}

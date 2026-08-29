'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { useToast } from '@/hooks/use-toast';
import { Send, Loader2 } from 'lucide-react';
import { useFirestore } from '@/firebase';
import { collection, addDoc } from 'firebase/firestore';
import { useTransition } from 'react';

const formSchema = z.object({
  name: z.string().trim().min(2, 'Please enter your full name.'),
  email: z.string().trim().email('Please enter a valid email address.'),
  phone: z.string().transform((value) => value.replace(/\D/g, '')).refine((value) => value.length === 10, 'Please enter a valid 10-digit phone number.'),
  subject: z.string().trim().min(5, 'Please enter a little more detail.'),
  message: z.string().trim().min(10, 'Please tell us a little more about your project.'),
});

export function ContactForm() {
  const { toast } = useToast();
  const firestore = useFirestore();
  const [isPending, startTransition] = useTransition();

  const form = useForm<z.input<typeof formSchema>, unknown, z.output<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: '', email: '', phone: '', subject: '', message: '' },
  });

  function onSubmit(values: z.output<typeof formSchema>) {
    if (!firestore) {
      toast({ variant: 'destructive', title: 'Unable to connect', description: 'Please try again in a moment or call us directly.' });
      return;
    }

    startTransition(async () => {
      try {
        await addDoc(collection(firestore, 'contact-messages'), {
          ...values,
          createdAt: new Date(),
          read: false,
        });
        toast({ title: 'Message sent', description: 'Thank you. We will get back to you shortly.' });
        form.reset();
      } catch (error) {
        console.error('Error saving message:', error);
        toast({ variant: 'destructive', title: 'Message not sent', description: 'Please try again or contact us by phone or email.' });
      }
    });
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6" noValidate>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField control={form.control} name="name" render={({ field }) => (
            <FormItem>
              <FormLabel>Full Name</FormLabel>
              <FormControl><Input autoComplete="name" placeholder="Your name" {...field} disabled={isPending} /></FormControl>
              <FormMessage />
            </FormItem>
          )} />
          <FormField control={form.control} name="email" render={({ field }) => (
            <FormItem>
              <FormLabel>Email Address</FormLabel>
              <FormControl><Input type="email" inputMode="email" autoComplete="email" placeholder="you@example.com" {...field} disabled={isPending} /></FormControl>
              <FormMessage />
            </FormItem>
          )} />
        </div>
        <FormField control={form.control} name="phone" render={({ field }) => (
          <FormItem>
            <FormLabel>Phone Number</FormLabel>
            <FormControl><Input type="tel" inputMode="tel" autoComplete="tel" placeholder="9876543210" maxLength={15} {...field} disabled={isPending} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <FormField control={form.control} name="subject" render={({ field }) => (
          <FormItem>
            <FormLabel>What can we help you with?</FormLabel>
            <FormControl><Input placeholder="New home, renovation, commercial project..." {...field} disabled={isPending} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <FormField control={form.control} name="message" render={({ field }) => (
          <FormItem>
            <FormLabel>Project Details</FormLabel>
            <FormControl><Textarea placeholder="Tell us about your project, location, approximate size, and what you need help with..." className="min-h-[150px]" {...field} disabled={isPending} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit" size="lg" className="w-full font-semibold" disabled={isPending}>
          {isPending ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Sending...</> : <><Send className="mr-2 h-4 w-4" /> Send Project Enquiry</>}
        </Button>
      </form>
    </Form>
  );
}

import type { Metadata } from 'next';
import { Inter, Manrope } from 'next/font/google';
import './globals.css';
import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { Toaster } from '@/components/ui/toaster';
import { cn } from '@/lib/utils';
import { FirebaseClientProvider } from '@/firebase/client-provider';

const bodyFont = Inter({ subsets: ['latin'], variable: '--font-body', display: 'swap' });
const headingFont = Manrope({ subsets: ['latin'], variable: '--font-headline', display: 'swap', weight: ['500', '600', '700', '800'] });
const siteUrl = 'https://www.dreamspacebuilders12.com';

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: { default: 'Dreamspace Builders | Construction & Design in Karnataka', template: '%s | Dreamspace Builders' },
  description: 'Dreamspace Builders provides residential, commercial and industrial construction, contracting, estimation, supervision, drafting, interior design and turnkey project services in Davangere, Bengaluru, Tumkur, Hiriyur and Bellary, Karnataka.',
  keywords: ['Dreamspace Builders','construction company Davangere','construction company Bengaluru','construction company Tumkur','construction company Hiriyur','construction company Bellary','residential construction Karnataka','commercial construction Karnataka','interior design Karnataka','turnkey construction Karnataka'],
  alternates: { canonical: '/' },
  openGraph: { type: 'website', url: siteUrl, siteName: 'Dreamspace Builders', title: 'Dreamspace Builders | Construction & Design in Karnataka', description: 'Construction, contracting, estimation, supervision, drafting, interior design and turnkey project services in Davangere, Bengaluru, Tumkur, Hiriyur and Bellary, Karnataka.', locale: 'en_IN' },
  robots: { index: true, follow: true },
};

const businessSchema = {
  '@context': 'https://schema.org', '@type': ['LocalBusiness', 'GeneralContractor'], name: 'Dreamspace Builders', url: siteUrl, telephone: '+91 9008592532', email: 'Dreamspacebuilders12@gmail.com',
  address: { '@type': 'PostalAddress', streetAddress: '#70/7, 15th Cross Road, Nijalingappa Layout', addressLocality: 'Davanagere', postalCode: '577004', addressRegion: 'Karnataka', addressCountry: 'IN' },
  areaServed: ['Davangere, Karnataka, India', 'Bengaluru, Karnataka, India', 'Tumkur, Karnataka, India', 'Hiriyur, Karnataka, India', 'Bellary, Karnataka, India'], description: 'Construction and design services for residential, commercial and industrial projects across Davangere, Bengaluru, Tumkur, Hiriyur and Bellary, Karnataka.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en-IN" className={cn(bodyFont.variable, headingFont.variable)}>
      <body className="font-body bg-background text-foreground antialiased">
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(businessSchema) }} />
        <FirebaseClientProvider>
          <div className="relative flex min-h-screen flex-col">
            <Header />
            <main className="flex-1">{children}</main>
            <Footer />
          </div>
          <Toaster />
        </FirebaseClientProvider>
      </body>
    </html>
  );
}


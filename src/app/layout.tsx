import type { Metadata } from 'next';
import { Inter, Manrope } from 'next/font/google';
import './globals.css';
import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { Toaster } from '@/components/ui/toaster';
import { cn } from '@/lib/utils';
import { FirebaseClientProvider } from '@/firebase/client-provider';
import { HomeDesignReferenceSlider } from '@/components/home-design-reference-slider';

const bodyFont = Inter({ subsets: ['latin'], variable: '--font-body', display: 'swap' });
const headingFont = Manrope({ subsets: ['latin'], variable: '--font-headline', display: 'swap', weight: ['500', '600', '700', '800'] });
const siteUrl = 'https://www.dreamspacebuilders12.com';

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: { default: 'Dreamspace Builders | Construction & Design in Davanagere', template: '%s | Dreamspace Builders' },
  description: 'Dreamspace Builders provides residential, commercial and industrial construction, contracting, estimation, supervision, drafting, interior design and turnkey project services in Davanagere, Karnataka.',
  keywords: ['Dreamspace Builders','construction company Davanagere','building construction Davanagere','residential construction Davanagere','commercial construction Davanagere','interior design Davanagere','turnkey construction Davanagere','construction contractor Karnataka'],
  alternates: { canonical: '/' },
  openGraph: { type: 'website', url: siteUrl, siteName: 'Dreamspace Builders', title: 'Dreamspace Builders | Construction & Design in Davanagere', description: 'Construction, contracting, estimation, supervision, drafting, interior design and turnkey project services in Davanagere, Karnataka.', locale: 'en_IN' },
  robots: { index: true, follow: true },
};

const businessSchema = {
  '@context': 'https://schema.org', '@type': ['LocalBusiness', 'GeneralContractor'], name: 'Dreamspace Builders', url: siteUrl, telephone: '+91 9008592532', email: 'Dreamspacebuilders12@gmail.com',
  address: { '@type': 'PostalAddress', streetAddress: '#70/7, 15th Cross Road, Nijalingappa Layout', addressLocality: 'Davanagere', postalCode: '577004', addressRegion: 'Karnataka', addressCountry: 'IN' },
  areaServed: 'Davanagere, Karnataka, India', description: 'Construction and design services for residential, commercial and industrial projects.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en-IN" className={cn(bodyFont.variable, headingFont.variable)}>
      <body className="font-body bg-background text-foreground antialiased">
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(businessSchema) }} />
        <FirebaseClientProvider>
          <div className="relative flex min-h-screen flex-col">
            <Header />
            <main className="flex-1">{children}<HomeDesignReferenceSlider /></main>
            <Footer />
          </div>
          <Toaster />
        </FirebaseClientProvider>
      </body>
    </html>
  );
}

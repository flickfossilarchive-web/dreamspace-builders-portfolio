import type { Metadata } from 'next';
import './globals.css';
import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { Toaster } from '@/components/ui/toaster';
import { cn } from '@/lib/utils';
import { FirebaseClientProvider } from '@/firebase/client-provider';

const siteUrl = 'https://www.dreamspacebuilders12.com';

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: 'Dreamspace Builders | Construction & Design in Davanagere',
    template: '%s | Dreamspace Builders',
  },
  description:
    'Dreamspace Builders provides residential, commercial and industrial construction, contracting, estimation, supervision, drafting, interior design and turnkey project services in Davanagere, Karnataka.',
  keywords: [
    'Dreamspace Builders',
    'construction company Davanagere',
    'building construction Davanagere',
    'residential construction Davanagere',
    'commercial construction Davanagere',
    'interior design Davanagere',
    'turnkey construction Davanagere',
    'construction contractor Karnataka',
  ],
  alternates: { canonical: '/' },
  openGraph: {
    type: 'website',
    url: siteUrl,
    siteName: 'Dreamspace Builders',
    title: 'Dreamspace Builders | Construction & Design in Davanagere',
    description:
      'Construction, contracting, estimation, supervision, drafting, interior design and turnkey project services in Davanagere, Karnataka.',
    locale: 'en_IN',
  },
  robots: {
    index: true,
    follow: true,
  },
};

const businessSchema = {
  '@context': 'https://schema.org',
  '@type': ['LocalBusiness', 'GeneralContractor'],
  name: 'Dreamspace Builders',
  url: siteUrl,
  telephone: '+91 9008592532',
  email: 'Dreamspacebuilders12@gmail.com',
  address: {
    '@type': 'PostalAddress',
    streetAddress: '#70/7, 15th Cross Road, Nijalingappa Layout',
    addressLocality: 'Davanagere',
    postalCode: '577004',
    addressRegion: 'Karnataka',
    addressCountry: 'IN',
  },
  areaServed: 'Davanagere, Karnataka, India',
  description:
    'Construction and design services for residential, commercial and industrial projects.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en-IN">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
      </head>
      <body className={cn('font-body bg-background text-foreground antialiased')}>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(businessSchema) }}
        />
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

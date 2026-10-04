import type { Metadata } from 'next';

const siteUrl = 'https://www.dreamspacebuilders12.com';

export const metadata: Metadata = {
  title: 'Contact',
  description: 'Contact Dreamspace Builders for construction, contracting, estimation, supervision, drafting, interior design and turnkey project enquiries in Davangere, Bengaluru, Tumkur, Hiriyur and Bellary.',
  alternates: { canonical: `${siteUrl}/contact` },
  openGraph: {
    type: 'website',
    url: `${siteUrl}/contact`,
    siteName: 'Dreamspace Builders',
    title: 'Contact | Dreamspace Builders',
    description: 'Contact Dreamspace Builders for construction and design project enquiries in Davangere, Bengaluru, Tumkur, Hiriyur and Bellary.',
    locale: 'en_IN',
  },
};

export default function ContactLayout({ children }: { children: React.ReactNode }) {
  return children;
}


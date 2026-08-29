import type { Metadata } from 'next';

const siteUrl = 'https://www.dreamspacebuilders12.com';

export const metadata: Metadata = {
  title: 'Contact',
  description: 'Contact Dreamspace Builders in Davanagere for construction, contracting, estimation, supervision, drafting, interior design and turnkey project enquiries.',
  alternates: { canonical: `${siteUrl}/contact` },
  openGraph: {
    type: 'website',
    url: `${siteUrl}/contact`,
    siteName: 'Dreamspace Builders',
    title: 'Contact | Dreamspace Builders',
    description: 'Contact Dreamspace Builders in Davanagere for construction and design project enquiries.',
    locale: 'en_IN',
  },
};

export default function ContactLayout({ children }: { children: React.ReactNode }) {
  return children;
}

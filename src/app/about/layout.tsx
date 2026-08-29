import type { Metadata } from 'next';

const siteUrl = 'https://www.dreamspacebuilders12.com';

export const metadata: Metadata = {
  title: 'About',
  description: 'Learn about Dreamspace Builders, a construction and design company serving residential, commercial and industrial projects in Davanagere, Karnataka.',
  alternates: { canonical: `${siteUrl}/about` },
  openGraph: {
    type: 'website',
    url: `${siteUrl}/about`,
    siteName: 'Dreamspace Builders',
    title: 'About | Dreamspace Builders',
    description: 'Learn about Dreamspace Builders and our construction and design services in Davanagere, Karnataka.',
    locale: 'en_IN',
  },
};

export default function AboutLayout({ children }: { children: React.ReactNode }) {
  return children;
}

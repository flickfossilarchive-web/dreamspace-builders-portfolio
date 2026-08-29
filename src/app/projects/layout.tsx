import type { Metadata } from 'next';

const siteUrl = 'https://www.dreamspacebuilders12.com';

export const metadata: Metadata = {
  title: 'Projects',
  description: 'Explore residential, commercial and industrial construction projects by Dreamspace Builders in Davanagere, Karnataka.',
  alternates: { canonical: `${siteUrl}/projects` },
  openGraph: {
    type: 'website',
    url: `${siteUrl}/projects`,
    siteName: 'Dreamspace Builders',
    title: 'Projects | Dreamspace Builders',
    description: 'Explore residential, commercial and industrial construction projects by Dreamspace Builders in Davanagere, Karnataka.',
    locale: 'en_IN',
  },
};

export default function ProjectsLayout({ children }: { children: React.ReactNode }) {
  return children;
}

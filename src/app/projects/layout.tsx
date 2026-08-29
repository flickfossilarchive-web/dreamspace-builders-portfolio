import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Projects',
  description: 'Explore Dreamspace Builders projects across residential, commercial and industrial construction in Davanagere, Karnataka.',
};

export default function ProjectsLayout({ children }: { children: React.ReactNode }) {
  return children;
}

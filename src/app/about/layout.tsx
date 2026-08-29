import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'About Us',
  description: 'Learn about Dreamspace Builders, our construction and design approach, and the values behind our work in Davanagere, Karnataka.',
};

export default function AboutLayout({ children }: { children: React.ReactNode }) {
  return children;
}

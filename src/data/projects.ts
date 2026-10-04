import type { Project } from '@/lib/types';

export const PORTFOLIO_PROJECTS: Project[] = [
  {
    id: 'bengaluru-contemporary-residence',
    title: 'Contemporary Residential Home — Bengaluru',
    description: 'A completed residential project in Bengaluru, presented through exterior views of contemporary homes with layered facades, open terraces, material contrasts and warm architectural lighting.',
    imageUrl: '/projects/bengaluru-contemporary-residence/cover.jpg',
    galleryUrls: [
      '/projects/bengaluru-contemporary-residence/home-01.jpg',
      '/projects/bengaluru-contemporary-residence/home-02.jpg',
      '/projects/bengaluru-contemporary-residence/home-03.jpg',
      '/projects/bengaluru-contemporary-residence/home-04.jpg',
      '/projects/bengaluru-contemporary-residence/home-05.jpg',
      '/projects/bengaluru-contemporary-residence/home-06.jpg',
      '/projects/bengaluru-contemporary-residence/home-07.jpg',
    ],
    category: 'Residential',
    status: 'Completed',
    location: 'Bengaluru, Karnataka',
    scope: 'Residential design and construction in Bengaluru, featuring contemporary home exteriors, multi-level facades, balcony and terrace spaces, mixed exterior finishes, and architectural lighting.',
    highlights: [
      'Layered facade designs with a mix of warm and contemporary materials.',
      'Balconies and terraces that extend the living spaces outdoors.',
      'Architectural lighting and landscaped street-facing details.',
    ],
    approach: 'The visual language balances clean geometry with warm timber tones, stone textures, glass railings, and considered exterior lighting.',
    tags: ['Bengaluru', 'Residential', 'Contemporary design', 'House exterior'],
    featured: true,
    visible: true,
  },
];

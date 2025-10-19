import type { Project } from './types';
import placeholderImages from '@/lib/placeholder-images.json';

const { project1, project2, project3, project4, project5, project6 } = placeholderImages;

export const projects: Project[] = [
  {
    id: '1',
    title: 'Modern Downtown Skyscraper',
    description: 'A 50-story mixed-use skyscraper featuring a sleek glass facade and luxury amenities. It has redefined the city skyline.',
    image: project1.src,
    imageMeta: project1,
    category: 'Commercial',
    tags: ['modern', 'skyscraper', 'sustainable'],
    featured: true,
  },
  {
    id: '2',
    title: 'Lakeside Family Home',
    description: 'A custom-built residential home with panoramic lake views, an open-concept living space, and natural wood finishes throughout.',
    image: project2.src,
    imageMeta: project2,
    category: 'Residential',
    tags: ['family', 'lakefront', 'modern'],
    featured: true,
  },
  {
    id: '3',
    title: 'Advanced Research Facility',
    description: 'State-of-the-art industrial complex designed for scientific research, featuring controlled environments and heavy-duty infrastructure.',
    image: project3.src,
    imageMeta: project3,
    category: 'Industrial',
    tags: ['tech', 'research', 'industrial'],
    featured: true,
  },
  {
    id: '4',
    title: 'Historic Theatre Restoration',
    description: 'A meticulous restoration of a 1920s theatre, preserving its historic architecture while upgrading it with modern acoustics and seating.',
    image: project4.src,
    imageMeta: project4,
    category: 'Commercial',
    tags: ['restoration', 'historic', 'community'],
  },
  {
    id: '5',
    title: 'Suburban Housing Development',
    description: 'A planned community of 50 single-family homes with shared green spaces, playgrounds, and a community center.',
    image: project5.src,
    imageMeta: project5,
    category: 'Residential',
    tags: ['community', 'suburban', 'family'],
  },
    {
    id: '6',
    title: 'Eco-Friendly Office Park',
    description: 'A corporate campus designed with sustainability in mind, featuring solar panels, green roofs, and rainwater harvesting systems.',
    image: project6.src,
    imageMeta: project6,
    category: 'Commercial',
    tags: ['sustainable', 'modern', 'corporate'],
  },
];

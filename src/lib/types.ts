export type Project = {
  id: string;
  title: string;
  description: string;
  image: string;
  category: 'Residential' | 'Commercial' | 'Industrial';
  tags: string[];
  featured?: boolean;
};

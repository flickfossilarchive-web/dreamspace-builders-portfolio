export type Project = {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
  category: 'Residential' | 'Commercial' | 'Industrial';
  tags: string[];
  featured?: boolean;
};

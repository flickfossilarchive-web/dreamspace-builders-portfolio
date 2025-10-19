export type Project = {
  id: string;
  title: string;
  description: string;
  image: string;
  imageMeta?: {
    src: string;
    width: number;
    height: number;
    alt: string;
    hint: string;
  };
  category: 'Residential' | 'Commercial' | 'Industrial';
  tags: string[];
  featured?: boolean;
};

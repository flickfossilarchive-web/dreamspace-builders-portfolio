export type Project = {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
  category: 'Residential' | 'Commercial' | 'Industrial';
  tags: string[];
  featured?: boolean;
};

export type ContactMessage = {
  id?: string;
  name: string;
  email: string;
  subject: string;
  message: string;
  createdAt: Date;
};

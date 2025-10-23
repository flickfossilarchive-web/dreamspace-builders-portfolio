import type { Timestamp } from "firebase/firestore";

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
  phone?: string;
  subject: string;
  message: string;
  createdAt: Timestamp;
  read: boolean;
};

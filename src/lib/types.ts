import type { Timestamp } from "firebase/firestore";

export type ProjectStatus = 'Completed' | 'Ongoing' | 'Planned';

export type Project = {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
  galleryUrls?: string[];
  category: 'Residential' | 'Commercial' | 'Industrial';
  status?: ProjectStatus;
  location?: string;
  completionYear?: number;
  area?: string;
  scope?: string;
  highlights?: string[];
  challenges?: string;
  approach?: string;
  tags: string[];
  featured?: boolean;
  visible?: boolean;
  createdAt?: Timestamp;
  updatedAt?: Timestamp;
};

export type ContactMessage = {
  id?: string;
  name: string;
  email: string;
  phone: string;
  subject: string;
  message: string;
  createdAt: Timestamp;
  read: boolean;
};

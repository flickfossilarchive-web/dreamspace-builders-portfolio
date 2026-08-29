import type { MetadataRoute } from 'next';

const siteUrl = 'https://www.dreamspacebuilders12.com';

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: siteUrl, changeFrequency: 'monthly', priority: 1 },
    { url: `${siteUrl}/about`, changeFrequency: 'yearly', priority: 0.8 },
    { url: `${siteUrl}/projects`, changeFrequency: 'weekly', priority: 0.9 },
    { url: `${siteUrl}/contact`, changeFrequency: 'yearly', priority: 0.9 },
  ];
}

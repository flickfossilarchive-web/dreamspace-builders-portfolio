import { ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

const projectSourceUrl = 'https://github.com/flickfossilarchive-web/dreamspace-builders-portfolio/blob/main/src/data/projects.ts';

export default function AddProjectDashboardPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div><p className="eyebrow">Portfolio management</p><h1 className="mt-2 text-3xl font-bold font-headline text-foreground">Add New Project</h1><p className="mt-2 text-muted-foreground">Portfolio content is stored with the website and deployed through Vercel.</p></div>
      <Card className="rounded-2xl border shadow-sm"><CardHeader><CardTitle>Manage project content</CardTitle><CardDescription>Project details are versioned with the site source. Images are served from the website’s own public assets.</CardDescription></CardHeader><CardContent className="space-y-5"><p className="leading-7 text-muted-foreground">Add or update a project record and its image paths in the project data file, add the images under the public projects folder, then deploy the site through Vercel.</p><Button asChild className="rounded-xl"><a href={projectSourceUrl} target="_blank" rel="noreferrer">Open project data <ExternalLink className="ml-2 h-4 w-4" /></a></Button></CardContent></Card>
    </div>
  );
}
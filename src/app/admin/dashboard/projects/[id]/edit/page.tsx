import Link from 'next/link';
import { ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

const projectSourceUrl = 'https://github.com/flickfossilarchive-web/dreamspace-builders-portfolio/blob/main/src/data/projects.ts';

export default function EditProjectPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <Button asChild variant="ghost"><Link href="/admin/dashboard/projects">Back to projects</Link></Button>
      <Card className="rounded-2xl"><CardContent className="space-y-5 py-12"><p className="eyebrow">Vercel portfolio</p><h1 className="font-headline text-3xl font-bold">Projects are managed with the site source</h1><p className="leading-7 text-muted-foreground">Project content and photos are deployed from the Vercel-connected repository. Update the project data and local image assets there, then deploy the changes.</p><Button asChild className="rounded-xl"><a href={projectSourceUrl} target="_blank" rel="noreferrer">Open project data <ExternalLink className="ml-2 h-4 w-4" /></a></Button></CardContent></Card>
    </div>
  );
}
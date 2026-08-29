'use client';

import { useEffect, useMemo, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { doc, getDoc, getFirestore, updateDoc, serverTimestamp } from 'firebase/firestore';
import { useFirebaseApp } from '@/firebase';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Loader2, Save, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { useToast } from '@/hooks/use-toast';

type EditableProject = {
  title: string; description: string; location: string; area: string; scope: string;
  challenges: string; approach: string; completionYear: string; highlights: string;
  tags: string; status: 'Completed' | 'Ongoing' | 'Planned'; featured: boolean; visible: boolean;
};

export default function EditProjectPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const app = useFirebaseApp();
  const firestore = useMemo(() => app ? getFirestore(app) : null, [app]);
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<EditableProject>({ title: '', description: '', location: '', area: '', scope: '', challenges: '', approach: '', completionYear: '', highlights: '', tags: '', status: 'Completed', featured: false, visible: true });

  useEffect(() => {
    if (!firestore || !params.id) return;
    (async () => {
      try {
        const snapshot = await getDoc(doc(firestore, 'projects', params.id));
        if (!snapshot.exists()) { setError('Project not found.'); return; }
        const data = snapshot.data();
        setForm({
          title: data.title ?? '', description: data.description ?? '', location: data.location ?? '', area: data.area ?? '',
          scope: data.scope ?? '', challenges: data.challenges ?? '', approach: data.approach ?? '', completionYear: data.completionYear ? String(data.completionYear) : '',
          highlights: Array.isArray(data.highlights) ? data.highlights.join('\n') : '', tags: Array.isArray(data.tags) ? data.tags.join(', ') : '',
          status: data.status ?? 'Completed', featured: data.featured === true, visible: data.visible !== false,
        });
      } catch (err) { setError(err instanceof Error ? err.message : 'Could not load project.'); }
      finally { setLoading(false); }
    })();
  }, [firestore, params.id]);

  const set = <K extends keyof EditableProject>(key: K, value: EditableProject[K]) => setForm((current) => ({ ...current, [key]: value }));

  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!firestore || !params.id) return;
    setSaving(true); setError(null);
    try {
      await updateDoc(doc(firestore, 'projects', params.id), {
        title: form.title.trim(), description: form.description.trim(), location: form.location.trim(), area: form.area.trim() || null,
        scope: form.scope.trim(), challenges: form.challenges.trim() || null, approach: form.approach.trim() || null,
        completionYear: form.completionYear ? Number(form.completionYear) : null,
        highlights: form.highlights.split('\n').map((item) => item.trim()).filter(Boolean),
        tags: form.tags.split(',').map((item) => item.trim()).filter(Boolean), status: form.status,
        featured: form.featured, visible: form.visible, updatedAt: serverTimestamp(),
      });
      toast({ title: 'Project updated', description: `${form.title} was saved successfully.` });
      router.push('/admin/dashboard/projects');
    } catch (err) { const message = err instanceof Error ? err.message : 'Could not save project.'; setError(message); toast({ variant: 'destructive', title: 'Save failed', description: message }); }
    finally { setSaving(false); }
  };

  if (loading) return <div className="flex min-h-[60vh] items-center justify-center"><Loader2 className="h-7 w-7 animate-spin text-primary" /></div>;
  if (error && !form.title) return <div className="space-y-5"><Button asChild variant="ghost"><Link href="/admin/dashboard/projects"><ArrowLeft className="mr-2 h-4 w-4" />Back to projects</Link></Button><Card><CardContent className="py-16 text-center text-destructive">{error}</CardContent></Card></div>;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-center justify-between gap-4"><div><p className="eyebrow">Portfolio management</p><h1 className="mt-2 font-headline text-4xl font-bold">Edit project</h1><p className="mt-2 text-muted-foreground">Update project facts, story and publishing controls. Existing images are preserved.</p></div><Button asChild variant="outline" className="rounded-xl"><Link href="/admin/dashboard/projects"><ArrowLeft className="mr-2 h-4 w-4" />Back</Link></Button></div>
      <form onSubmit={save} className="space-y-6">
        <Card className="rounded-2xl"><CardHeader><CardTitle>Project details</CardTitle></CardHeader><CardContent className="grid gap-5 md:grid-cols-2">
          <div className="space-y-2 md:col-span-2"><Label>Project name</Label><Input value={form.title} onChange={(e) => set('title', e.target.value)} required /></div>
          <div className="space-y-2 md:col-span-2"><Label>Overview</Label><Textarea className="min-h-32" value={form.description} onChange={(e) => set('description', e.target.value)} required /></div>
          <div className="space-y-2"><Label>Location</Label><Input value={form.location} onChange={(e) => set('location', e.target.value)} /></div>
          <div className="space-y-2"><Label>Completion year</Label><Input type="number" value={form.completionYear} onChange={(e) => set('completionYear', e.target.value)} /></div>
          <div className="space-y-2"><Label>Project area</Label><Input value={form.area} onChange={(e) => set('area', e.target.value)} /></div>
          <div className="space-y-2"><Label>Status</Label><select className="h-10 w-full rounded-md border bg-background px-3" value={form.status} onChange={(e) => set('status', e.target.value as EditableProject['status'])}><option>Completed</option><option>Ongoing</option><option>Planned</option></select></div>
          <div className="space-y-2 md:col-span-2"><Label>Scope</Label><Textarea value={form.scope} onChange={(e) => set('scope', e.target.value)} /></div>
        </CardContent></Card>
        <Card className="rounded-2xl"><CardHeader><CardTitle>Case-study story</CardTitle></CardHeader><CardContent className="space-y-5">
          <div className="space-y-2"><Label>Key highlights — one per line</Label><Textarea value={form.highlights} onChange={(e) => set('highlights', e.target.value)} /></div>
          <div className="grid gap-5 md:grid-cols-2"><div className="space-y-2"><Label>Challenges</Label><Textarea value={form.challenges} onChange={(e) => set('challenges', e.target.value)} /></div><div className="space-y-2"><Label>Our approach</Label><Textarea value={form.approach} onChange={(e) => set('approach', e.target.value)} /></div></div>
          <div className="space-y-2"><Label>Tags</Label><Input value={form.tags} onChange={(e) => set('tags', e.target.value)} /><p className="text-xs text-muted-foreground">Separate tags with commas.</p></div>
        </CardContent></Card>
        <Card className="rounded-2xl"><CardHeader><CardTitle>Publishing</CardTitle></CardHeader><CardContent className="grid gap-4 md:grid-cols-2"><label className="flex items-start gap-3 rounded-xl border p-4"><input type="checkbox" checked={form.featured} onChange={(e) => set('featured', e.target.checked)} /><span><strong>Feature on homepage</strong><span className="mt-1 block text-sm text-muted-foreground">Use for the strongest projects.</span></span></label><label className="flex items-start gap-3 rounded-xl border p-4"><input type="checkbox" checked={form.visible} onChange={(e) => set('visible', e.target.checked)} /><span><strong>Publish in portfolio</strong><span className="mt-1 block text-sm text-muted-foreground">Turn off to keep this project private.</span></span></label></CardContent></Card>
        {error && <p className="rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">{error}</p>}
        <div className="flex justify-end"><Button type="submit" size="lg" className="rounded-xl" disabled={saving}>{saving ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Saving…</> : <><Save className="mr-2 h-4 w-4" />Save changes</>}</Button></div>
      </form>
    </div>
  );
}

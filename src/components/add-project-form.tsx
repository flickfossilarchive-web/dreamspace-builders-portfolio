'use client';

import { useMemo, useState, useTransition } from 'react';
import Image from 'next/image';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { addDoc, collection, getFirestore, serverTimestamp } from 'firebase/firestore';
import { getDownloadURL, getStorage, ref, uploadBytes } from 'firebase/storage';
import { useFirebaseApp, useUser } from '@/firebase';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { AlertCircle, ImagePlus, Loader2, Save, UploadCloud } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const MAX_IMAGE_SIZE = 5_000_000;
const MAX_GALLERY_IMAGES = 6;
const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

const formSchema = z.object({
  title: z.string().min(3, 'Project name is required.'),
  description: z.string().min(30, 'Add a meaningful project overview (at least 30 characters).'),
  category: z.enum(['Residential', 'Commercial', 'Industrial']),
  status: z.enum(['Completed', 'Ongoing', 'Planned']),
  location: z.string().min(2, 'Location is required.'),
  completionYear: z.string().optional(),
  area: z.string().optional(),
  scope: z.string().min(5, 'Describe the project scope.'),
  highlights: z.string().optional(),
  challenges: z.string().optional(),
  approach: z.string().optional(),
  tags: z.string().min(3, 'Add at least one tag.'),
  featured: z.boolean().default(false),
  visible: z.boolean().default(true),
  image: z.any().refine((files) => files?.length === 1, 'Cover image is required.'),
  gallery: z.any().optional(),
});

type FormValues = z.infer<typeof formSchema>;

function validateImages(files: File[], maxCount: number) {
  if (!files.length) return null;
  if (files.length > maxCount) return `Select up to ${maxCount} images.`;
  if (files.some((file) => !ACCEPTED_TYPES.includes(file.type))) return 'Use JPG, PNG or WebP images.';
  if (files.some((file) => file.size > MAX_IMAGE_SIZE)) return 'Each image must be 5MB or smaller.';
  return null;
}

export function AddProjectForm() {
  const [coverPreview, setCoverPreview] = useState<string | null>(null);
  const [galleryPreviews, setGalleryPreviews] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const { toast } = useToast();
  const { user } = useUser();
  const app = useFirebaseApp();
  const firestore = useMemo(() => (app ? getFirestore(app) : null), [app]);
  const storage = useMemo(() => (app ? getStorage(app) : null), [app]);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { title: '', description: '', category: 'Residential', status: 'Completed', location: '', completionYear: '', area: '', scope: '', highlights: '', challenges: '', approach: '', tags: '', featured: false, visible: true },
  });

  const onCoverChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return setCoverPreview(null);
    const message = validateImages([file], 1);
    if (message) { setError(message); event.target.value = ''; return; }
    setError(null);
    setCoverPreview(URL.createObjectURL(file));
  };

  const onGalleryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files ?? []);
    const message = validateImages(files, MAX_GALLERY_IMAGES);
    if (message) { setError(message); event.target.value = ''; return; }
    setError(null);
    setGalleryPreviews(files.map((file) => URL.createObjectURL(file)));
  };

  const onSubmit = (values: FormValues) => {
    if (!user || !firestore || !storage) { setError('Please sign in again before adding a project.'); return; }
    startTransition(async () => {
      setError(null);
      try {
        const coverFile = values.image[0] as File;
        const galleryFiles = Array.from((values.gallery as FileList | undefined) ?? []);
        const stamp = Date.now();
        const coverRef = ref(storage, `projects/${user.uid}/${stamp}_cover_${coverFile.name}`);
        const coverUpload = await uploadBytes(coverRef, coverFile, { contentType: coverFile.type });
        const imageUrl = await getDownloadURL(coverUpload.ref);
        const galleryUrls = await Promise.all(galleryFiles.map(async (file, index) => {
          const galleryRef = ref(storage, `projects/${user.uid}/${stamp}_gallery_${index}_${file.name}`);
          const upload = await uploadBytes(galleryRef, file, { contentType: file.type });
          return getDownloadURL(upload.ref);
        }));
        await addDoc(collection(firestore, 'projects'), {
          title: values.title.trim(), description: values.description.trim(), category: values.category, status: values.status,
          location: values.location.trim(), completionYear: values.completionYear ? Number(values.completionYear) : null,
          area: values.area?.trim() || null, scope: values.scope.trim(),
          highlights: values.highlights?.split('\n').map((item) => item.trim()).filter(Boolean) ?? [],
          challenges: values.challenges?.trim() || null, approach: values.approach?.trim() || null,
          tags: values.tags.split(',').map((tag) => tag.trim()).filter(Boolean), featured: values.featured, visible: values.visible,
          imageUrl, galleryUrls, authorUid: user.uid, createdAt: serverTimestamp(), updatedAt: serverTimestamp(),
        });
        toast({ title: 'Project published', description: `${values.title} is now available in your portfolio.` });
        form.reset(); setCoverPreview(null); setGalleryPreviews([]);
      } catch (submitError) {
        const message = submitError instanceof Error ? submitError.message : 'Could not save the project.';
        setError(message); toast({ variant: 'destructive', title: 'Could not save project', description: message });
      }
    });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <Card className="rounded-2xl border shadow-sm">
          <CardHeader><CardTitle className="flex items-center gap-2"><ImagePlus className="h-5 w-5 text-primary" />Project media</CardTitle><CardDescription>One cover image plus up to six supporting photos. JPG, PNG or WebP, max 5MB each.</CardDescription></CardHeader>
          <CardContent className="grid gap-6 lg:grid-cols-2">
            <FormField control={form.control} name="image" render={({ field }) => <FormItem><FormLabel>Cover image *</FormLabel><FormControl><label className="relative flex min-h-72 cursor-pointer items-center justify-center overflow-hidden rounded-2xl border-2 border-dashed bg-secondary/50 p-4 transition hover:border-primary/60">{coverPreview ? <Image src={coverPreview} alt="Cover preview" fill className="object-cover" sizes="(min-width: 1024px) 45vw, 100vw" /> : <div className="text-center"><UploadCloud className="mx-auto h-10 w-10 text-primary" /><p className="mt-3 font-semibold">Upload cover image</p><p className="mt-1 text-sm text-muted-foreground">Used on cards and the project hero.</p></div>}<Input {...field} type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={(event) => { field.onChange(event.target.files); onCoverChange(event); }} /></label></FormControl><FormMessage /></FormItem>} />
            <FormField control={form.control} name="gallery" render={({ field }) => <FormItem><FormLabel>Project gallery</FormLabel><FormControl><label className="flex min-h-72 cursor-pointer flex-col justify-center rounded-2xl border-2 border-dashed bg-secondary/30 p-5 transition hover:border-primary/60"><div className="flex items-center gap-3"><div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary"><ImagePlus className="h-5 w-5" /></div><div><p className="font-semibold">Add supporting photos</p><p className="text-sm text-muted-foreground">Up to {MAX_GALLERY_IMAGES} additional images.</p></div></div>{galleryPreviews.length > 0 && <div className="mt-5 grid grid-cols-3 gap-2">{galleryPreviews.map((preview, index) => <div key={preview} className="relative aspect-square overflow-hidden rounded-xl"><Image src={preview} alt={`Gallery preview ${index + 1}`} fill className="object-cover" sizes="120px" /></div>)}</div>}<Input {...field} type="file" multiple accept="image/jpeg,image/png,image/webp" className="hidden" onChange={(event) => { field.onChange(event.target.files); onGalleryChange(event); }} /></label></FormControl><FormMessage /></FormItem>} />
          </CardContent>
        </Card>

        <Card className="rounded-2xl border shadow-sm"><CardHeader><CardTitle>Project overview</CardTitle><CardDescription>Give visitors the facts they need to understand the work.</CardDescription></CardHeader><CardContent className="grid gap-5 md:grid-cols-2">
          <FormField control={form.control} name="title" render={({ field }) => <FormItem className="md:col-span-2"><FormLabel>Project name *</FormLabel><FormControl><Input placeholder="e.g. Contemporary Family Residence" {...field} /></FormControl><FormMessage /></FormItem>} />
          <FormField control={form.control} name="description" render={({ field }) => <FormItem className="md:col-span-2"><FormLabel>Short overview *</FormLabel><FormControl><Textarea className="min-h-32" placeholder="What was built, for whom, and what made the project distinctive?" {...field} /></FormControl><FormMessage /></FormItem>} />
          <FormField control={form.control} name="category" render={({ field }) => <FormItem><FormLabel>Category *</FormLabel><Select value={field.value} onValueChange={field.onChange}><FormControl><SelectTrigger><SelectValue /></SelectTrigger></FormControl><SelectContent><SelectItem value="Residential">Residential</SelectItem><SelectItem value="Commercial">Commercial</SelectItem><SelectItem value="Industrial">Industrial</SelectItem></SelectContent></Select><FormMessage /></FormItem>} />
          <FormField control={form.control} name="status" render={({ field }) => <FormItem><FormLabel>Status *</FormLabel><Select value={field.value} onValueChange={field.onChange}><FormControl><SelectTrigger><SelectValue /></SelectTrigger></FormControl><SelectContent><SelectItem value="Completed">Completed</SelectItem><SelectItem value="Ongoing">Ongoing</SelectItem><SelectItem value="Planned">Planned</SelectItem></SelectContent></Select><FormMessage /></FormItem>} />
          <FormField control={form.control} name="location" render={({ field }) => <FormItem><FormLabel>Location *</FormLabel><FormControl><Input placeholder="Davanagere, Karnataka" {...field} /></FormControl><FormMessage /></FormItem>} />
          <FormField control={form.control} name="completionYear" render={({ field }) => <FormItem><FormLabel>Completion year</FormLabel><FormControl><Input type="number" min="2000" max="2100" placeholder="2026" {...field} /></FormControl><FormMessage /></FormItem>} />
          <FormField control={form.control} name="area" render={({ field }) => <FormItem><FormLabel>Built-up / project area</FormLabel><FormControl><Input placeholder="e.g. 2,400 sq. ft." {...field} /></FormControl><FormMessage /></FormItem>} />
          <FormField control={form.control} name="scope" render={({ field }) => <FormItem className="md:col-span-2"><FormLabel>Project scope *</FormLabel><FormControl><Textarea className="min-h-28" placeholder="Construction, supervision, interiors, turnkey execution..." {...field} /></FormControl><FormMessage /></FormItem>} />
        </CardContent></Card>

        <Card className="rounded-2xl border shadow-sm"><CardHeader><CardTitle>Project story</CardTitle><CardDescription>Optional detail that turns a gallery into a useful case study.</CardDescription></CardHeader><CardContent className="space-y-5">
          <FormField control={form.control} name="highlights" render={({ field }) => <FormItem><FormLabel>Key highlights</FormLabel><FormControl><Textarea className="min-h-28" placeholder={'One highlight per line\nCustom elevation and finishes\nEnd-to-end supervision'} {...field} /></FormControl><FormMessage /></FormItem>} />
          <div className="grid gap-5 md:grid-cols-2"><FormField control={form.control} name="challenges" render={({ field }) => <FormItem><FormLabel>Challenges</FormLabel><FormControl><Textarea placeholder="What needed special attention?" {...field} /></FormControl><FormMessage /></FormItem>} /><FormField control={form.control} name="approach" render={({ field }) => <FormItem><FormLabel>Our approach</FormLabel><FormControl><Textarea placeholder="How the team planned and executed the work." {...field} /></FormControl><FormMessage /></FormItem>} /></div>
        </CardContent></Card>

        <Card className="rounded-2xl border shadow-sm"><CardHeader><CardTitle>Search & publishing</CardTitle><CardDescription>Control how the project appears across the portfolio.</CardDescription></CardHeader><CardContent className="space-y-5">
          <FormField control={form.control} name="tags" render={({ field }) => <FormItem><FormLabel>Tags *</FormLabel><FormControl><Input placeholder="villa, turnkey, modern, interior" {...field} /></FormControl><p className="text-xs text-muted-foreground">Separate tags with commas.</p><FormMessage /></FormItem>} />
          <div className="grid gap-4 md:grid-cols-2"><FormField control={form.control} name="featured" render={({ field }) => <FormItem className="flex items-start gap-3 rounded-xl border p-4"><FormControl><Checkbox checked={field.value} onCheckedChange={field.onChange} /></FormControl><div><FormLabel>Feature on homepage</FormLabel><p className="text-sm text-muted-foreground">Use for your strongest work.</p></div></FormItem>} /><FormField control={form.control} name="visible" render={({ field }) => <FormItem className="flex items-start gap-3 rounded-xl border p-4"><FormControl><Checkbox checked={field.value} onCheckedChange={field.onChange} /></FormControl><div><FormLabel>Publish in portfolio</FormLabel><p className="text-sm text-muted-foreground">Turn off while preparing a project.</p></div></FormItem>} /></div>
        </CardContent></Card>

        {error && <Alert variant="destructive"><AlertCircle className="h-4 w-4" /><AlertTitle>Couldn’t save project</AlertTitle><AlertDescription>{error}</AlertDescription></Alert>}
        <div className="flex flex-col gap-3 border-t pt-6 sm:flex-row sm:items-center sm:justify-between"><p className="text-sm text-muted-foreground">Real project photos and specific facts make the strongest portfolio entries.</p><Button type="submit" disabled={isPending} size="lg" className="rounded-xl px-7 font-semibold">{isPending ? <><Loader2 className="mr-2 h-5 w-5 animate-spin" />Publishing…</> : <><Save className="mr-2 h-5 w-5" />Publish project</>}</Button></div>
      </form>
    </Form>
  );
}

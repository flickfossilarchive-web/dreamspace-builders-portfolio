'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useState, useMemo, useTransition } from 'react';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { UploadCloud, AlertCircle, Sparkles, Image as ImageIcon, X } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { getStorage, ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { collection, addDoc, getFirestore } from 'firebase/firestore';
import { useUser, useFirebaseApp } from '@/firebase';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Checkbox } from '@/components/ui/checkbox';


const MAX_IMAGES = 3;
const MAX_FILE_SIZE = 5_000_000; // 5MB
const ACCEPTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

const formSchema = z.object({
  title: z.string().min(5, 'Title must be at least 5 characters.'),
  description: z.string().min(10, 'Description must be at least 10 characters.'),
  category: z.enum(['Residential', 'Commercial', 'Industrial']),
  tags: z.string().min(3, 'Please provide at least one tag.'),
  featured: z.boolean().default(false),
  images: z.any()
    .refine(files => files?.length > 0, 'At least one image is required.')
    .refine(files => files?.length <= MAX_IMAGES, `You can upload a maximum of ${MAX_IMAGES} images.`)
    .refine(files => Array.from(files).every((file: any) => file.size <= MAX_FILE_SIZE), `Max file size is 5MB.`)
    .refine(
      files => Array.from(files).every((file: any) => ACCEPTED_IMAGE_TYPES.includes(file.type)),
      '.jpg, .jpeg, .png, .webp and .gif files are accepted.'
    ),
});

type FormValues = z.infer<typeof formSchema>;

export function AddProjectForm() {
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();
  const { user } = useUser();
  const app = useFirebaseApp();
  const firestore = useMemo(() => app ? getFirestore(app) : null, [app]);
  const storage = useMemo(() => app ? getStorage(app) : null, [app]);


  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: '',
      description: '',
      category: 'Residential',
      tags: '',
      featured: false,
    },
  });

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      const newPreviews: string[] = [];
      const fileArray = Array.from(files);
      
      form.setValue('images', fileArray);

      fileArray.forEach(file => {
        const reader = new FileReader();
        reader.onloadend = () => {
          newPreviews.push(reader.result as string);
          if(newPreviews.length === fileArray.length) {
            setImagePreviews(newPreviews);
          }
        };
        reader.readAsDataURL(file);
      });
    } else {
      setImagePreviews([]);
      form.setValue('images', []);
    }
  };

  const onSubmit = (values: FormValues) => {
    if (!user || !firestore || !storage) {
      setError('You must be logged in to add a project.');
      return;
    }

    startTransition(async () => {
      setError(null);
      try {
        // 1. Upload images to Firebase Storage
        const imageFiles = values.images;
        const imageUrls: string[] = [];
        
        for (const imageFile of imageFiles) {
            const storageRef = ref(storage, `projects/${user.uid}/${Date.now()}_${imageFile.name}`);
            const uploadResult = await uploadBytes(storageRef, imageFile);
            const imageUrl = await getDownloadURL(uploadResult.ref);
            imageUrls.push(imageUrl);
        }

        // 2. Add project data to Firestore
        await addDoc(collection(firestore, 'projects'), {
          title: values.title,
          description: values.description,
          category: values.category,
          tags: values.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
          featured: values.featured,
          imageUrls,
          authorUid: user.uid,
          createdAt: new Date(),
        });
        
        toast({
          title: 'Project Added!',
          description: `${values.title} has been successfully added to your portfolio.`,
        });
        form.reset();
        setImagePreviews([]);

      } catch (e: any) {
        console.error('Error adding project:', e);
        setError(e.message || 'An error occurred while adding the project.');
        toast({
          variant: 'destructive',
          title: 'Uh oh! Something went wrong.',
          description: e.message || 'Could not save the project.',
        });
      }
    });
  };

  return (
    <Form {...form}>
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
      <FormField
          control={form.control}
          name="images"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-lg">Project Images</FormLabel>
              <FormControl>
                <div 
                  className="relative flex justify-center items-center w-full h-64 border-2 border-dashed border-border rounded-lg cursor-pointer hover:bg-muted/50 transition-colors bg-card"
                  onClick={() => document.getElementById('image-input')?.click()}
                >
                  {imagePreviews.length > 0 ? (
                     <div className="grid grid-cols-3 gap-2 p-2 h-full w-full">
                      {imagePreviews.map((src, index) => (
                        <div key={index} className="relative h-full w-full">
                           <Image src={src} alt={`Preview ${index + 1}`} fill objectFit="contain" className="rounded-md" />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center text-muted-foreground">
                      <UploadCloud className="mx-auto h-12 w-12" />
                      <p className="mt-2 font-semibold">Click to upload or drag and drop</p>
                      <p className="text-xs mt-1">Up to {MAX_IMAGES} images (PNG, JPG, GIF, max 5MB each)</p>
                    </div>
                  )}
                   <Input
                      id="image-input"
                      type="file"
                      accept="image/*"
                      multiple
                      className="hidden"
                      onBlur={field.onBlur}
                      name={field.name}
                      onChange={handleImageChange}
                      ref={field.ref}
                    />
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

      <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-lg">Project Title</FormLabel>
              <FormControl>
                <Input placeholder="e.g., Modern Downtown Skyscraper" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

      <FormField
        control={form.control}
        name="description"
        render={({ field }) => (
            <FormItem>
            <FormLabel className="text-lg">Project Description</FormLabel>
            <FormControl>
                <Textarea
                placeholder="A 50-story mixed-use skyscraper featuring a sleek glass facade..."
                className="min-h-[150px] text-base"
                {...field}
                />
            </FormControl>
            <FormMessage />
            </FormItem>
        )}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <FormField
            control={form.control}
            name="category"
            render={({ field }) => (
                <FormItem>
                <FormLabel className="text-lg">Category</FormLabel>
                 <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a category" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="Residential">Residential</SelectItem>
                      <SelectItem value="Commercial">Commercial</SelectItem>
                      <SelectItem value="Industrial">Industrial</SelectItem>
                    </SelectContent>
                  </Select>
                <FormMessage />
                </FormItem>
            )}
            />
        <FormField
            control={form.control}
            name="tags"
            render={({ field }) => (
                <FormItem>
                <FormLabel className="text-lg">Tags</FormLabel>
                <FormControl>
                    <Input placeholder="e.g., modern, skyscraper, sustainable" {...field} />
                </FormControl>
                 <p className="text-xs text-muted-foreground">Separate tags with commas.</p>
                <FormMessage />
                </FormItem>
            )}
            />
      </div>
      
       <FormField
        control={form.control}
        name="featured"
        render={({ field }) => (
          <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4 shadow">
            <FormControl>
              <Checkbox
                checked={field.value}
                onCheckedChange={field.onChange}
              />
            </FormControl>
            <div className="space-y-1 leading-none">
              <FormLabel>
                Feature this project?
              </FormLabel>
              <p className="text-sm text-muted-foreground">
                Featured projects will be displayed prominently on the homepage.
              </p>
            </div>
          </FormItem>
        )}
      />
      
      {error && (
        <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Button type="submit" disabled={isPending} size="lg" className="w-full font-semibold">
        {isPending ? (
          <>
            <Sparkles className="mr-2 h-5 w-5 animate-spin" />
            Adding Project...
          </>
        ) : (
          'Add Project'
        )}
      </Button>
    </form>
    </Form>
  );
}

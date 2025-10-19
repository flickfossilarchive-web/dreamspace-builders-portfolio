'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useState, useRef, useTransition } from 'react';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { UploadCloud, AlertCircle, Sparkles } from 'lucide-react';
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


const formSchema = z.object({
  title: z.string().min(5, 'Title must be at least 5 characters.'),
  description: z.string().min(10, 'Description must be at least 10 characters.'),
  category: z.enum(['Residential', 'Commercial', 'Industrial']),
  tags: z.string().min(3, 'Please provide at least one tag.'),
  featured: z.boolean().default(false),
  image: z.any()
    .refine(files => files?.length == 1, 'Image is required.')
    .refine(files => files?.[0]?.size <= 5_000_000, `Max file size is 5MB.`)
    .refine(
      files => ['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(files?.[0]?.type),
      '.jpg, .jpeg, .png, .webp and .gif files are accepted.'
    ),
});

type FormValues = z.infer<typeof formSchema>;

export function AddProjectForm() {
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();
  const { user } = useUser();
  const app = useFirebaseApp();
  const firestore = useMemo(() => getFirestore(app!), [app]);
  const storage = useMemo(() => getStorage(app!), [app]);


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
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setImagePreview(null);
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
        // 1. Upload image to Firebase Storage
        const imageFile = values.image[0];
        const storageRef = ref(storage, `projects/${user.uid}/${Date.now()}_${imageFile.name}`);
        const uploadResult = await uploadBytes(storageRef, imageFile);
        const imageUrl = await getDownloadURL(uploadResult.ref);

        // 2. Add project data to Firestore
        await addDoc(collection(firestore, 'projects'), {
          title: values.title,
          description: values.description,
          category: values.category,
          tags: values.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
          featured: values.featured,
          imageUrl,
          authorUid: user.uid,
          createdAt: new Date(),
        });
        
        toast({
          title: 'Project Added!',
          description: `${values.title} has been successfully added to your portfolio.`,
        });
        form.reset();
        setImagePreview(null);

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
          name="image"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-lg">Project Image</FormLabel>
              <FormControl>
                <div 
                  className="relative flex justify-center items-center w-full h-64 border-2 border-dashed border-border/80 rounded-lg cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => document.getElementById('image-input')?.click()}
                >
                  {imagePreview ? (
                    <Image src={imagePreview} alt="Image preview" layout="fill" objectFit="contain" className="rounded-lg p-2" />
                  ) : (
                    <div className="text-center text-muted-foreground">
                      <UploadCloud className="mx-auto h-12 w-12" />
                      <p className="mt-2 font-semibold">Click to upload or drag and drop</p>
                      <p className="text-xs mt-1">PNG, JPG, or GIF (Max 5MB)</p>
                    </div>
                  )}
                   <Input
                      id="image-input"
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onBlur={field.onBlur}
                      name={field.name}
                      onChange={(e) => {
                        field.onChange(e.target.files);
                        handleImageChange(e);
                      }}
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

      <Button type="submit" disabled={isPending} size="lg" className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold">
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

'use client';

import { useFormState, useFormStatus } from 'react-dom';
import { useEffect, useRef, useState } from 'react';
import Image from 'next/image';
import { createProjectDescription, type State } from '@/lib/actions';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Sparkles, UploadCloud, ClipboardCopy, Check, AlertCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Card, CardContent } from '@/components/ui/card';

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <Button type="submit" disabled={pending} className="w-full bg-accent hover:bg-accent/90">
      {pending ? (
        <>
          <Sparkles className="mr-2 h-4 w-4 animate-spin" />
          Generating...
        </>
      ) : (
        <>
          <Sparkles className="mr-2 h-4 w-4" />
          Generate Description
        </>
      )}
    </Button>
  );
}

export function AddProjectForm() {
  const initialState: State = { message: null, errors: {} };
  const [state, dispatch] = useFormState(createProjectDescription, initialState);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  
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
  
  const handleCopyToClipboard = () => {
    if (state.description) {
        navigator.clipboard.writeText(state.description);
        toast({
            title: "Copied to Clipboard",
            description: "The project description has been copied.",
        });
    }
  };

  useEffect(() => {
    if (state.message === 'success' && state.description) {
      toast({
        title: "Success!",
        description: "Project description generated.",
        variant: "default",
      })
    }
  }, [state, toast])

  return (
    <form action={dispatch} className="space-y-8">
      <div className="space-y-2">
        <Label htmlFor="image">Project Image</Label>
        <div 
          className="relative flex justify-center items-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer hover:bg-muted/50 transition-colors"
          onClick={() => fileInputRef.current?.click()}
        >
          {imagePreview ? (
            <Image src={imagePreview} alt="Image preview" layout="fill" objectFit="contain" className="rounded-lg p-2" />
          ) : (
            <div className="text-center text-muted-foreground">
              <UploadCloud className="mx-auto h-12 w-12" />
              <p className="mt-2">Click to upload or drag and drop</p>
              <p className="text-xs">PNG, JPG, GIF up to 10MB</p>
            </div>
          )}
        </div>
        <Input
          id="image"
          name="image"
          type="file"
          accept="image/*"
          ref={fileInputRef}
          className="hidden"
          onChange={handleImageChange}
        />
        {state.errors?.image && (
          <p className="text-sm font-medium text-destructive">{state.errors.image[0]}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="constructionData">Construction Data</Label>
        <Textarea
          id="constructionData"
          name="constructionData"
          placeholder="e.g., 50-story mixed-use skyscraper, glass facade, sustainable energy systems, luxury amenities..."
          className="min-h-[150px]"
        />
        {state.errors?.constructionData && (
          <p className="text-sm font-medium text-destructive">{state.errors.constructionData[0]}</p>
        )}
      </div>
      
      {state.message && state.message !== 'success' && (
        <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{state.message}</AlertDescription>
        </Alert>
      )}

      <SubmitButton />

      {state.description && (
        <div className="space-y-4 pt-4 border-t">
          <h3 className="text-xl font-headline text-primary">Generated Description</h3>
           <Card className="bg-secondary">
            <CardContent className="p-4 relative">
              <p className="text-secondary-foreground whitespace-pre-wrap">{state.description}</p>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute top-2 right-2 h-7 w-7"
                onClick={handleCopyToClipboard}
              >
                <ClipboardCopy className="h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </form>
  );
}

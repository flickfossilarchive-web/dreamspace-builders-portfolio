'use server';

import { z } from 'zod';
import { generateProjectDescription } from '@/ai/flows/generate-project-description';

const FormSchema = z.object({
  constructionData: z.string().min(10, {
    message: 'Construction data must be at least 10 characters.',
  }),
});

export type State = {
  errors?: {
    constructionData?: string[];
    image?: string[];
  };
  message?: string | null;
  description?: string | null;
};

// Helper to convert a File to a Base64 data URI
async function fileToDataURI(file: File) {
  const arrayBuffer = await file.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);
  return `data:${file.type};base64,${buffer.toString('base64')}`;
}


export async function createProjectDescription(prevState: State, formData: FormData): Promise<State> {
  const validatedFields = FormSchema.safeParse({
    constructionData: formData.get('constructionData'),
  });

  const imageFile = formData.get('image') as File;

  if (!imageFile || imageFile.size === 0) {
    return {
      errors: { image: ['Please upload an image of the project.'] },
      message: 'Image is required.',
    };
  }
  
  // Basic validation for image type
  if (!imageFile.type.startsWith('image/')) {
    return {
        errors: { image: ['Please upload a valid image file (PNG, JPG, etc.).'] },
        message: 'Invalid file type.',
    };
  }

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
      message: 'Failed to validate fields.',
    };
  }
  
  try {
    const imageDataUri = await fileToDataURI(imageFile);
    
    const result = await generateProjectDescription({
        imageDataUri: imageDataUri,
        constructionData: validatedFields.data.constructionData,
    });

    if (result.projectDescription) {
        return { message: 'success', description: result.projectDescription };
    } else {
        return { message: 'AI generation failed to produce a description.' };
    }

  } catch (e) {
    console.error(e);
    return { message: 'An error occurred during description generation.' };
  }
}

import { AddProjectForm } from '@/components/add-project-form';

export default function AddProjectPage() {
  return (
    <div className="container mx-auto px-4 py-16 md:py-24">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold font-headline text-primary">AI Project Description Generator</h1>
          <p className="mt-4 text-lg text-muted-foreground">
            Upload a project image and provide some key data points. Our AI will craft a compelling description for you.
          </p>
        </div>

        <div className="bg-card p-8 rounded-lg shadow-md border">
            <AddProjectForm />
        </div>
      </div>
    </div>
  );
}

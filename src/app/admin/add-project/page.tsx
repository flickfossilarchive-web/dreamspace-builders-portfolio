import { AddProjectForm } from '@/components/add-project-form';

export default function AddProjectPage() {
  return (
    <div className="container mx-auto px-4 py-16 md:py-24">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-bold font-headline text-primary">AI Project Description Generator</h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload a project image and provide key details. Our AI will craft a compelling, professional description for your portfolio.
          </p>
        </div>

        <div className="bg-secondary p-8 rounded-lg shadow-lg border border-border/60">
            <AddProjectForm />
        </div>
      </div>
    </div>
  );
}

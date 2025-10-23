'use client';
import { AddProjectForm } from '@/components/add-project-form';

export default function AddProjectPage() {
  return (
    <div>
        <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold font-headline text-foreground">Add New Project</h1>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Fill out the form below to add a new project to your portfolio.
            </p>
        </div>
        <div className="bg-card p-8 rounded-lg shadow-lg border max-w-4xl mx-auto">
            <AddProjectForm />
        </div>
    </div>
  );
}

'use client';
import { AddProjectForm } from '@/components/add-project-form';

export default function AddProjectDashboardPage() {
  return (
     <div>
        <div className="text-left mb-8">
            <h1 className="text-3xl font-bold font-headline text-foreground">Add New Project</h1>
            <p className="mt-2 text-md text-muted-foreground">
                Fill out the form below to add a new project to the portfolio.
            </p>
        </div>
        <div className="bg-card p-8 rounded-lg shadow-lg border max-w-4xl">
            <AddProjectForm />
        </div>
    </div>
  );
}

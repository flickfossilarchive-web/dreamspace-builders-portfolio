'use client';
import { AddProjectForm } from '@/components/add-project-form';
import { useUser, useAuth } from '@/firebase';
import { GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { Button } from '@/components/ui/button';
import { FcGoogle } from 'react-icons/fc';

export default function AddProjectPage() {
  const { user, loading } = useUser();
  const auth = useAuth();

  const handleSignIn = async () => {
    if (!auth) return;
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
    } catch (error) {
      console.error('Error signing in with Google', error);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-16 md:py-24 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
        <p className="mt-4 text-muted-foreground">Loading...</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-16 md:py-24">
      <div className="max-w-3xl mx-auto">
        {user ? (
          <>
            <div className="text-center mb-12">
              <h1 className="text-5xl md:text-6xl font-bold font-headline text-primary">Add New Project</h1>
              <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
                Fill out the form below to add a new project to your portfolio.
              </p>
            </div>
            <div className="bg-secondary p-8 rounded-lg shadow-lg border border-border/60">
              <AddProjectForm />
            </div>
          </>
        ) : (
          <div className="text-center">
            <h1 className="text-4xl font-bold font-headline text-primary mb-4">Admin Access Required</h1>
            <p className="text-lg text-muted-foreground mb-8">Please sign in to add a new project.</p>
            <Button onClick={handleSignIn} size="lg">
              <FcGoogle className="mr-2 h-5 w-5" />
              Sign in with Google
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

'use client';
import { useMemo } from 'react';
import { FirebaseProvider } from './provider';
import { initializeFirebase } from './';
import { firebaseConfig } from './config';

export function FirebaseClientProvider({ children }: { children: React.ReactNode }) {
  const firebaseMemo = useMemo(() => {
    // Validate that the required Firebase environment variables are set on the client.
    if (
      !firebaseConfig.apiKey ||
      !firebaseConfig.authDomain ||
      !firebaseConfig.projectId
    ) {
      // In a real-world application, you would want to handle this error more gracefully.
      // For this project, we'll throw an error to make it clear that the configuration is missing.
       console.error(
        'Firebase environment variables are not set. Please add them to your .env file.'
      );
      return { firebaseApp: null, firestore: null, auth: null };
    }
    return initializeFirebase();
  }, []);

  return (
    <FirebaseProvider 
      firebaseApp={firebaseMemo.firebaseApp} 
      firestore={firebaseMemo.firestore} 
      auth={firebaseMemo.auth}
    >
      {children}
    </FirebaseProvider>
  );
}

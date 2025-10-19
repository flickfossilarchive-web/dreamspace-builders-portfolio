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
      // Don't initialize firebase if the config is not present
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

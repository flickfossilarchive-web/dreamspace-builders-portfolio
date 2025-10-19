'use client';
import { useMemo } from 'react';
import { FirebaseProvider } from './provider';
import { initializeFirebase } from './';

export function FirebaseClientProvider({ children }: { children: React.ReactNode }) {
  const { firebaseApp, firestore, auth } = useMemo(() => initializeFirebase(), []);

  return (
    <FirebaseProvider firebaseApp={firebaseApp} firestore={firestore} auth={auth}>
      {children}
    </FirebaseProvider>
  );
}

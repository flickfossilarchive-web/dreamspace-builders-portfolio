import { initializeApp, getApps, getApp, type FirebaseApp } from 'firebase/app';
import { getAuth, type Auth } from 'firebase/auth';
import { getFirestore, type Firestore } from 'firebase/firestore';
import { firebaseConfig } from './config';

import { useCollection } from './firestore/use-collection';
import { useDoc } from './firestore/use-doc';
import {
  useFirebase,
  useFirebaseApp,
  useFirestore,
  useAuth,
} from './provider';
import { useUser } from './auth/use-user';

function initializeFirebase() {
  const isConfigured = getApps().length > 0;
  const firebaseApp = isConfigured ? getApp() : initializeApp(firebaseConfig);
  const firestore = getFirestore(firebaseApp);
  const auth = getAuth(firebaseApp);
  return { firebaseApp, firestore, auth };
}

export {
  useCollection,
  useDoc,
  useUser,
  useFirebase,
  useFirebaseApp,
  useFirestore,
  useAuth,
  initializeFirebase,
};

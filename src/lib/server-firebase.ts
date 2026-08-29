import { getApp, getApps, initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { firebaseConfig } from '@/firebase/config';

export function getServerFirestore() {
  const app = getApps().length ? getApp() : initializeApp(firebaseConfig);
  return getFirestore(app);
}

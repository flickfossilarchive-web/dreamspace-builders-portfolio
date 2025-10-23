'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle, LogIn } from 'lucide-react';

export default function AdminLoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    
    const adminUser = process.env.NEXT_PUBLIC_ADMIN_USERNAME;
    const adminPass = process.env.NEXT_PUBLIC_ADMIN_PASSWORD;

    if (!adminUser || !adminPass) {
        setError('Admin credentials are not configured on the server. Please contact support.');
        return;
    }

    if (username === adminUser && password === adminPass) {
      // In a real app, you'd use a more secure session management method.
      // For simplicity, we'll use sessionStorage.
      try {
        sessionStorage.setItem('admin-authenticated', 'true');
        router.push('/admin/dashboard/enquiries');
      } catch (e) {
        setError('Your browser does not support session storage. Please use a modern browser.');
      }
      setError(null);
    } else {
      setError('Invalid username or password.');
    }
  };

  return (
    <div className="container mx-auto px-4 py-16 md:py-24 flex items-center justify-center min-h-[calc(100vh-10rem)]">
        <Card className="max-w-md w-full mx-auto border shadow-lg">
        <CardHeader className="text-center">
            <CardTitle className="text-3xl font-headline text-foreground">Admin Dashboard</CardTitle>
            <CardDescription>Please enter your credentials to access the dashboard.</CardDescription>
        </CardHeader>
        <CardContent>
            <form onSubmit={handleLogin} className="space-y-6">
            <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                />
            </div>
            <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                />
            </div>
            {error && (
                <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Login Failed</AlertTitle>
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}
            <Button type="submit" className="w-full" size="lg">
                <LogIn className="mr-2 h-5 w-5" />
                Login
            </Button>
            </form>
        </CardContent>
        </Card>
    </div>
  );
}

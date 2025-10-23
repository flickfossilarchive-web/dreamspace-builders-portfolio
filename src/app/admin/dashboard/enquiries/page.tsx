'use client'
import { useState, useMemo, useEffect } from 'react';
import { useFirestore, useCollection } from '@/firebase';
import { collection, orderBy, query, writeBatch, doc, where } from 'firebase/firestore';
import type { ContactMessage } from '@/lib/types';
import { format } from 'date-fns';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from '@/components/ui/input';
import { Search } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

export default function EnquiriesPage() {
    const firestore = useFirestore();
    const [searchTerm, setSearchTerm] = useState('');

    const enquiriesQuery = useMemo(() => {
        if (!firestore) return null;
        return query(collection(firestore, 'contact-messages'), orderBy('createdAt', 'desc'));
    }, [firestore]);

    const { data: enquiries, loading } = useCollection<ContactMessage>(enquiriesQuery);
    
    // Mark messages as read when the component mounts
    useEffect(() => {
        if (firestore && enquiries) {
            const unread = enquiries.filter(e => !e.read && e.id);
            if (unread.length > 0) {
                const batch = writeBatch(firestore);
                unread.forEach(msg => {
                    const docRef = doc(firestore, 'contact-messages', msg.id!);
                    batch.update(docRef, { read: true });
                });
                batch.commit().catch(console.error);
            }
        }
    }, [firestore, enquiries]);


    const filteredEnquiries = useMemo(() => {
        if (!enquiries) return [];
        return enquiries.filter(enquiry => 
            enquiry.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            enquiry.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
            enquiry.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
            enquiry.message.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [enquiries, searchTerm]);

    return (
        <Card>
            <CardHeader>
                <CardTitle>Contact Enquiries</CardTitle>
                <CardDescription>Messages submitted through the contact form.</CardDescription>
                <div className="relative pt-4">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                    <Input
                        type="text"
                        placeholder="Search enquiries..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full max-w-sm pl-10 bg-background"
                    />
                </div>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                        <TableHead className="w-[150px]">Date</TableHead>
                        <TableHead>Name</TableHead>
                        <TableHead>Email</TableHead>
                        <TableHead>Subject</TableHead>
                        <TableHead className="w-[40%]">Message</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                             [...Array(5)].map((_, i) => (
                                <TableRow key={i}>
                                    <TableCell><Skeleton className="h-5 w-full" /></TableCell>
                                    <TableCell><Skeleton className="h-5 w-full" /></TableCell>
                                    <TableCell><Skeleton className="h-5 w-full" /></TableCell>
                                    <TableCell><Skeleton className="h-5 w-full" /></TableCell>
                                    <TableCell><Skeleton className="h-5 w-full" /></TableCell>
                                </TableRow>
                            ))
                        ) : filteredEnquiries.length > 0 ? (
                            filteredEnquiries.map((enquiry) => (
                                <TableRow key={enquiry.id} className={!enquiry.read ? 'bg-primary/5' : ''}>
                                    <TableCell className="font-medium text-xs">
                                        {enquiry.createdAt ? format(new Date(enquiry.createdAt.seconds * 1000), 'PPp') : 'N/A'}
                                    </TableCell>
                                    <TableCell>{enquiry.name}</TableCell>
                                    <TableCell>{enquiry.email}</TableCell>
                                    <TableCell>{enquiry.subject}</TableCell>
                                    <TableCell className="text-muted-foreground truncate max-w-xs">{enquiry.message}</TableCell>
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell colSpan={5} className="h-24 text-center">
                                    No enquiries found.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    )
}

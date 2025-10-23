'use client'
import { useState, useMemo, useEffect } from 'react';
import { useFirestore, useCollection } from '@/firebase';
import { collection, orderBy, query, writeBatch, doc, where } from 'firebase/firestore';
import type { ContactMessage } from '@/lib/types';
import { format, startOfWeek, endOfWeek, startOfMonth, endOfMonth, startOfYear, endOfYear } from 'date-fns';
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
import { Search, Calendar as CalendarIcon } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { DateRange } from 'react-day-picker';
import { cn } from '@/lib/utils';

type DateFilter = 'all' | 'week' | 'month' | 'year' | 'custom';

export default function EnquiriesPage() {
    const firestore = useFirestore();
    const [searchTerm, setSearchTerm] = useState('');
    const [date, setDate] = useState<DateRange | undefined>();
    const [activeFilter, setActiveFilter] = useState<DateFilter>('all');


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

    const setDateFilter = (filter: DateFilter) => {
        const now = new Date();
        setActiveFilter(filter);
        if (filter === 'week') {
            setDate({ from: startOfWeek(now), to: endOfWeek(now) });
        } else if (filter === 'month') {
            setDate({ from: startOfMonth(now), to: endOfMonth(now) });
        } else if (filter === 'year') {
            setDate({ from: startOfYear(now), to: endOfYear(now) });
        } else {
            setDate(undefined);
        }
    }

    const filteredEnquiries = useMemo(() => {
        if (!enquiries) return [];
        
        let dateFiltered = enquiries;

        if (date?.from) {
             const from = date.from.getTime();
             const to = date.to ? date.to.getTime() : new Date().getTime();

             dateFiltered = enquiries.filter(enquiry => {
                 if (!enquiry.createdAt) return false;
                 const enquiryDate = enquiry.createdAt.seconds * 1000;
                 return enquiryDate >= from && enquiryDate <= to;
             });
        }


        if (!searchTerm) {
            return dateFiltered;
        }

        return dateFiltered.filter(enquiry => 
            enquiry.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            enquiry.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
            enquiry.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
            enquiry.message.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [enquiries, searchTerm, date]);

    return (
        <Card>
            <CardHeader>
                <CardTitle>Contact Enquiries</CardTitle>
                <CardDescription>Messages submitted through the contact form.</CardDescription>
                <div className="flex flex-col md:flex-row gap-4 items-center pt-4">
                    <div className="relative flex-1 w-full md:w-auto">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                        <Input
                            type="text"
                            placeholder="Search enquiries..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full max-w-sm pl-10 bg-background"
                        />
                    </div>
                    <div className="flex gap-2 items-center flex-wrap">
                        <Button variant={activeFilter === 'all' ? 'default' : 'outline'} onClick={() => setDateFilter('all')}>All</Button>
                        <Button variant={activeFilter === 'week' ? 'default' : 'outline'} onClick={() => setDateFilter('week')}>This Week</Button>
                        <Button variant={activeFilter === 'month' ? 'default' : 'outline'} onClick={() => setDateFilter('month')}>This Month</Button>
                        <Button variant={activeFilter === 'year' ? 'default' : 'outline'} onClick={() => setDateFilter('year')}>This Year</Button>
                         <Popover>
                            <PopoverTrigger asChild>
                            <Button
                                id="date"
                                variant={"outline"}
                                className={cn(
                                    "w-[240px] justify-start text-left font-normal",
                                    !date && "text-muted-foreground",
                                    activeFilter === 'custom' && "border-primary"
                                )}
                            >
                                <CalendarIcon className="mr-2 h-4 w-4" />
                                {date?.from ? (
                                date.to ? (
                                    <>
                                    {format(date.from, "LLL dd, y")} -{" "}
                                    {format(date.to, "LLL dd, y")}
                                    </>
                                ) : (
                                    format(date.from, "LLL dd, y")
                                )
                                ) : (
                                <span>Custom date</span>
                                )}
                            </Button>
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-0" align="end">
                            <Calendar
                                initialFocus
                                mode="range"
                                defaultMonth={date?.from}
                                selected={date}
                                onSelect={(range) => { setDate(range); setActiveFilter('custom'); }}
                                numberOfMonths={2}
                            />
                            </PopoverContent>
                        </Popover>
                    </div>
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
                                    No enquiries found for the selected criteria.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    )
}

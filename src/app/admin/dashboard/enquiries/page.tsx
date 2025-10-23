'use client'
import { useState, useMemo, useEffect } from 'react';
import { useFirestore, useCollection } from '@/firebase';
import { collection, orderBy, query, writeBatch, doc, where, deleteDoc } from 'firebase/firestore';
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
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

import { Input } from '@/components/ui/input';
import { Search, Calendar as CalendarIcon, FileDown, Trash2 } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { DateRange } from 'react-day-picker';
import { cn } from '@/lib/utils';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { useToast } from '@/hooks/use-toast';


type DateFilter = 'all' | 'week' | 'month' | 'year' | 'custom';

export default function EnquiriesPage() {
    const firestore = useFirestore();
    const { toast } = useToast();
    const [searchTerm, setSearchTerm] = useState('');
    const [date, setDate] = useState<DateRange | undefined>();
    const [activeFilter, setActiveFilter] = useState<DateFilter>('all');
    const [enquiryToDelete, setEnquiryToDelete] = useState<string | null>(null);


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
            (enquiry.phone && enquiry.phone.toLowerCase().includes(searchTerm.toLowerCase())) ||
            enquiry.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
            enquiry.message.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [enquiries, searchTerm, date]);

    const handleExportCSV = () => {
        const headers = ['Date', 'Name', 'Email', 'Phone', 'Subject', 'Message'];
        const rows = filteredEnquiries.map(e => [
            e.createdAt ? format(new Date(e.createdAt.seconds * 1000), 'yyyy-MM-dd HH:mm:ss') : 'N/A',
            `"${e.name.replace(/"/g, '""')}"`,
            `"${e.email.replace(/"/g, '""')}"`,
            `"${e.phone ? e.phone.replace(/"/g, '""') : ''}"`,
            `"${e.subject.replace(/"/g, '""')}"`,
            `"${e.message.replace(/"/g, '""')}"`,
        ]);

        const csvContent = "data:text/csv;charset=utf-8," 
            + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
        
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "enquiries.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleExportPDF = () => {
        const doc = new jsPDF();
        
        autoTable(doc, {
            head: [['Date', 'Name', 'Email', 'Phone', 'Subject', 'Message']],
            body: filteredEnquiries.map(e => [
                e.createdAt ? format(new Date(e.createdAt.seconds * 1000), 'PPp') : 'N/A',
                e.name,
                e.email,
                e.phone || '',
                e.subject,
                e.message
            ]),
            styles: {
                fontSize: 8,
            },
            headStyles: {
                fillColor: [22, 163, 74]
            },
            columnStyles: {
                5: { cellWidth: 70 }
            }
        });

        doc.save('enquiries.pdf');
    };
    
    const handleDelete = async () => {
        if (!firestore || !enquiryToDelete) return;
        
        const docRef = doc(firestore, 'contact-messages', enquiryToDelete);
        try {
            await deleteDoc(docRef);
            toast({
                title: 'Enquiry Deleted',
                description: 'The message has been permanently removed.',
            });
        } catch (error) {
            console.error('Error deleting enquiry:', error);
            toast({
                variant: 'destructive',
                title: 'Error',
                description: 'Could not delete the enquiry. Please try again.',
            });
        } finally {
            setEnquiryToDelete(null);
        }
    };


    return (
        <>
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
                            className="w-full max-w-xs pl-10 bg-background"
                        />
                    </div>
                    <div className="flex gap-2 items-center flex-wrap flex-1 justify-end">
                        <Button variant={activeFilter === 'all' ? 'default' : 'outline'} size="sm" onClick={() => setDateFilter('all')}>All</Button>
                        <Button variant={activeFilter === 'week' ? 'default' : 'outline'} size="sm" onClick={() => setDateFilter('week')}>Week</Button>
                        <Button variant={activeFilter === 'month' ? 'default' : 'outline'} size="sm" onClick={() => setDateFilter('month')}>Month</Button>
                        <Button variant={activeFilter === 'year' ? 'default' : 'outline'} size="sm" onClick={() => setDateFilter('year')}>Year</Button>
                         <Popover>
                            <PopoverTrigger asChild>
                            <Button
                                id="date"
                                variant={"outline"}
                                size="sm"
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
                         <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="outline" size="sm">
                                    <FileDown className="mr-2 h-4 w-4" />
                                    Export
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent>
                                <DropdownMenuItem onClick={handleExportCSV}>Export to CSV</DropdownMenuItem>
                                <DropdownMenuItem onClick={handleExportPDF}>Export to PDF</DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
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
                        <TableHead>Phone</TableHead>
                        <TableHead>Subject</TableHead>
                        <TableHead className="w-[30%]">Message</TableHead>
                        <TableHead>Actions</TableHead>
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
                                    <TableCell><Skeleton className="h-5 w-full" /></TableCell>
                                    <TableCell><Skeleton className="h-8 w-8" /></TableCell>
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
                                    <TableCell>{enquiry.phone || 'N/A'}</TableCell>
                                    <TableCell>{enquiry.subject}</TableCell>
                                    <TableCell className="text-muted-foreground truncate max-w-xs">{enquiry.message}</TableCell>
                                    <TableCell>
                                        <Button 
                                            variant="ghost" 
                                            size="icon"
                                            onClick={() => setEnquiryToDelete(enquiry.id!)}
                                        >
                                            <Trash2 className="h-4 w-4 text-destructive" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell colSpan={7} className="h-24 text-center">
                                    No enquiries found for the selected criteria.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
        <AlertDialog open={!!enquiryToDelete} onOpenChange={(open) => !open && setEnquiryToDelete(null)}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                    <AlertDialogDescription>
                        This action cannot be undone. This will permanently delete the enquiry
                        and remove the data from our servers.
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={handleDelete} className="bg-destructive hover:bg-destructive/90">Delete</AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
        </>
    )
}

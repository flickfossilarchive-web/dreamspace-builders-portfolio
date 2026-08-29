'use client';

import { useEffect, useState } from 'react';

type Props = { src: string; alt: string; className?: string; priority?: boolean };

export function ReferenceImage({ src, alt, className = '', priority = false }: Props) {
  const [resolvedSrc, setResolvedSrc] = useState<string | null>(null);

  useEffect(() => {
    let objectUrl: string | null = null;
    let cancelled = false;
    const load = async () => {
      try {
        const response = await fetch(src, { cache: 'force-cache' });
        if (!response.ok) throw new Error('Reference image unavailable');
        const bytes = new Uint8Array(await response.arrayBuffer());
        const isWebp = bytes.length >= 12 && bytes[0] === 0x52 && bytes[1] === 0x49 && bytes[2] === 0x46 && bytes[3] === 0x46 && bytes[8] === 0x57 && bytes[9] === 0x45 && bytes[10] === 0x42 && bytes[11] === 0x50;
        if (isWebp) {
          objectUrl = URL.createObjectURL(new Blob([bytes], { type: 'image/webp' }));
        } else {
          const encoded = new TextDecoder().decode(bytes).trim();
          const binary = atob(encoded);
          const decoded = new Uint8Array(binary.length);
          for (let i = 0; i < binary.length; i++) decoded[i] = binary.charCodeAt(i);
          objectUrl = URL.createObjectURL(new Blob([decoded], { type: 'image/webp' }));
        }
        if (!cancelled) setResolvedSrc(objectUrl);
      } catch {
        if (!cancelled) setResolvedSrc(null);
      }
    };
    load();
    return () => { cancelled = true; if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [src]);

  if (!resolvedSrc) return <div className={`animate-pulse bg-muted ${className}`} aria-label="Loading design reference" />;
  return <img src={resolvedSrc} alt={alt} className={className} loading={priority ? 'eager' : 'lazy'} decoding="async" />;
}

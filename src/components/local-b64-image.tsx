'use client';

import { useEffect, useState } from 'react';

type Props = {
  src: string;
  alt: string;
  className?: string;
  loading?: 'lazy' | 'eager';
  decoding?: 'async' | 'sync' | 'auto';
};

export function LocalB64Image({ src, alt, className, loading = 'lazy', decoding = 'async' }: Props) {
  const [dataUrl, setDataUrl] = useState('');

  useEffect(() => {
    let cancelled = false;
    fetch(src, { cache: 'force-cache' })
      .then(async (response) => {
        if (!response.ok) throw new Error(`Failed to load local image: ${response.status}`);
        const base64 = (await response.text()).trim();
        if (!base64.startsWith('UklGR')) throw new Error('Invalid local WebP payload');
        if (!cancelled) setDataUrl(`data:image/webp;base64,${base64}`);
      })
      .catch(() => {
        if (!cancelled) setDataUrl('');
      });

    return () => {
      cancelled = true;
    };
  }, [src]);

  if (!dataUrl) {
    return <div aria-label={alt} className={`${className ?? ''} bg-gradient-to-br from-slate-800 via-slate-700 to-slate-900`} role="img" />;
  }

  return <img src={dataUrl} alt={alt} loading={loading} decoding={decoding} className={className} />;
}

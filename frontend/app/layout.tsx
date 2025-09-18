import type { Metadata } from 'next';
import { IBM_Plex_Sans, Inter } from 'next/font/google';
import type { ReactNode } from 'react';
import './globals.css';
import { ToastProvider } from '@/providers/ToastProvider';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap' });
const plex = IBM_Plex_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-plex',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'SlashRun Workspace',
  description: 'Gotham-inspired investigative workspace for geopolitical simulations.',
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${plex.variable}`}
      suppressHydrationWarning
    >
      <body>
        <ToastProvider>{children}</ToastProvider>
      </body>
    </html>
  );
}

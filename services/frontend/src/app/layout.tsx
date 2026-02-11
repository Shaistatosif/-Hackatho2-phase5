import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Todo Chatbot | Phase V',
  description: 'AI-Powered Task Management with Natural Language',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-navy-900 min-h-screen`}>
        {children}
      </body>
    </html>
  );
}

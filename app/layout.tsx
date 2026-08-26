import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Aurum Advocacia | Estratégia Jurídica',
  description: 'Assessoria jurídica estratégica para empresas, famílias e patrimônios.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}

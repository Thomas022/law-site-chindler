import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Chindler | Administração de Imóveis',
  description: 'Administração de imóveis e condomínios, locação, compra e venda no Rio de Janeiro desde 1976.',
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

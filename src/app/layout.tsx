import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "shift. — Air Quality Dashboard",
  description: "Real-time smog prediction and air quality analytics by SmogNet",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-foreground">
        {children}
      </body>
    </html>
  );
}

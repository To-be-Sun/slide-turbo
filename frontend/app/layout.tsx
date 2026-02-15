import type React from "react";
import type { Metadata } from "next";
import {
  Inter,
  JetBrains_Mono,
  Noto_Sans_JP,
  Noto_Serif_JP,
  Poppins,
} from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";

const inter = Inter({ subsets: ["latin"] });
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});
const notoSansJp = Noto_Sans_JP({
  subsets: ["latin"],
  variable: "--font-slide-sans",
});
const notoSerifJp = Noto_Serif_JP({
  subsets: ["latin"],
  variable: "--font-slide-serif",
});
const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-slide-poppins",
});

export const metadata: Metadata = {
  title: "Slide Turbo",
  description: "AI でプレゼンテーションを高速作成",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja" className="dark">
      <body
        className={`${inter.className} ${jetbrainsMono.variable} ${notoSansJp.variable} ${notoSerifJp.variable} ${poppins.variable} font-sans antialiased`}
      >
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}

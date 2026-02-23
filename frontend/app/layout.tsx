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

// 使用するウェイトだけ指定してプリロード数を減らし「preload が使われない」警告を抑える
const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});
// モノスペースは一部でしか使わないため preload しない（警告抑制）
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400"],
  variable: "--font-mono",
  display: "swap",
  preload: false,
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

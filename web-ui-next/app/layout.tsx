import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Zomato AI Recommendations",
  description: "Next.js UI inspired by editorial discovery layout"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}


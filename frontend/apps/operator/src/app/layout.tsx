import type { Metadata } from "next";
import type { ReactNode } from "react";
import "@argus/ui/src/tokens.css";
import { Providers } from "./providers";

export const metadata: Metadata = { title: "Argus Operator" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

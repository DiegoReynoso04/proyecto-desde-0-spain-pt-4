import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "TallerYA — Talleres presenciales",
    template: "%s · TallerYA",
  },
  description: "Talleres presenciales de cocina, cerámica, música, pintura, dibujo y fotografía.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#F2F2F2",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="es">
      <body className="flex min-h-dvh flex-col">
        <a
          href="#contenido"
          className="sr-only rounded bg-ocre-400 px-4 py-3 font-semibold text-tinta-900 focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50"
        >
          Saltar al contenido
        </a>
        {children}
      </body>
    </html>
  );
}

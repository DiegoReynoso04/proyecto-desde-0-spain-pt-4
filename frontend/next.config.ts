import type { NextConfig } from "next";

// URL interna del backend. En Docker es http://backend:8000; fuera de Docker, localhost.
// Los rewrites se fijan en el build, por eso también se pasa como build arg.
const apiInternalUrl = (process.env.API_INTERNAL_URL ?? "http://localhost:8000").replace(/\/$/, "");

// Docker Desktop sobre Windows no propaga eventos del sistema de ficheros: usamos polling.
const usePolling = process.env.WATCHPACK_POLLING === "true";

const securityHeaders = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
];

const nextConfig: NextConfig = {
  output: "standalone",
  poweredByHeader: false,
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  ...(usePolling ? { watchOptions: { pollIntervalMs: 1000 } } : {}),
  // Todas las llamadas /api/* van a FastAPI desde el mismo origen (cookies first-party).
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${apiInternalUrl}/api/:path*` }];
  },
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
};

export default nextConfig;

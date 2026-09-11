/** @type {import('next').NextConfig} */
const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

const nextConfig = {
  reactStrictMode: true,
  // The FastAPI backend serves some routes with a trailing slash and others
  // without. Do NOT let Next.js normalize trailing slashes on /api/* paths,
  // otherwise /api/v1/agents/ gets 308-redirected to /api/v1/agents and the
  // backend then redirects back (absolute localhost URL) -> redirect loop.
  skipTrailingSlashRedirect: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;

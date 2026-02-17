/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  async rewrites() {
    // Only use rewrites in development
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/upload',
          destination: 'http://localhost:8080/upload',
        },
        {
          source: '/status/:job*',
          destination: 'http://localhost:8080/status/:job*',
        },
        {
          source: '/download/:job*',
          destination: 'http://localhost:8080/download/:job*',
        },
      ];
    }
    return [];
  },
};

module.exports = nextConfig; 
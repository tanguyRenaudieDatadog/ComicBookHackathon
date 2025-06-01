/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
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
  },
};

module.exports = nextConfig; 
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.BACKEND_URL || 'http://backend:8000'}/api/:path*`,
      },
      {
        source: '/health',
        destination: `${process.env.BACKEND_URL || 'http://backend:8000'}/health`,
      },
      {
        source: '/docs',
        destination: `${process.env.BACKEND_URL || 'http://backend:8000'}/docs`,
      },
    ]
  },
}

module.exports = nextConfig

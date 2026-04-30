/**
 * @type {import('next').NextConfig}
 */
const nextConfig = {
    async redirects() {
    return [
      {
        source: '/doctrine.html',
        destination: '/doctrines',
        permanent: true,
      },
      {
        source: '/about.html',
        destination: '/doctrines',
        permanent: true,
      },
      {
        source: '/index.html',
        destination: '/',
        permanent: true,
      },
      {
        source: '/media.html',
        destination: '/media',
        permanent: true,
      },
      {
        source: '/contact.html',
        destination: '/contact',
        permanent: true,
      },
      {
        source: '/event.html',
        destination: '/',
        permanent: true,
      },
    ]
  },
  output: 'export',
  // output: 'standalone',
  images: { unoptimized: true },
//  allowImportingTsExtensions: true,
  // Optional: Change links `/me` -> `/me/` and emit `/me.html` -> `/me/index.html`
  trailingSlash: true,

  // Optional: Prevent automatic `/me` -> `/me/`, instead preserve `href`
  skipTrailingSlashRedirect: true,

  // Optional: Change the output directory `out` -> `dist`
  // distDir: 'dist',
}

module.exports = nextConfig

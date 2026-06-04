/**
 * @type {import('next').NextConfig}
 */
const nextConfig = {
  // output: 'export',
  output: 'standalone',
  images: { unoptimized: true },
//  allowImportingTsExtensions: true,
  // Optional: Change links `/me` -> `/me/` and emit `/me.html` -> `/me/index.html`
  trailingSlash: true,

  // Optional: Prevent automatic `/me` -> `/me/`, instead preserve `href`
  skipTrailingSlashRedirect: true,

  // Optional: Change the output directory `out` -> `dist`
  // distDir: 'dist',
  experimental: { workerThreads: false, cpus: 2 }
}

module.exports = nextConfig

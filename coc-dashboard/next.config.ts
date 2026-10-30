import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Pin the project root: a stray lockfile higher up (e.g. in the home folder)
  // otherwise makes Turbopack pick that folder and miss file changes here.
  turbopack: {
    root: __dirname,
  },
};

export default nextConfig;

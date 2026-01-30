import type { NextConfig } from "next";
import path from "path";

const appDir = path.resolve(__dirname);

const nextConfig: NextConfig = {
  output: "standalone",
  turbopack: {
    root: appDir,
  },
};

export default nextConfig;

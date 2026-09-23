import type { NextConfig } from "next";

const config: NextConfig = {
  transpilePackages: ["@argus/ui", "@argus/api-client"],
  reactStrictMode: true,
};

export default config;

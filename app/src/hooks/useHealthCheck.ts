"use client";

import { useState, useEffect } from "react";
import { checkHealth } from "@/lib/api";

const POLL_INTERVAL_MS = 15_000;

export function useHealthCheck(): boolean {
  const [online, setOnline] = useState(false);

  useEffect(() => {
    const check = async () => {
      const healthy = await checkHealth();
      setOnline(healthy);
    };
    check();
    const interval = setInterval(check, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  return online;
}

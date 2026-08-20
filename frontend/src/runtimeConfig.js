function envFlag(value, fallback = false) {
  if (value == null || value === "") return fallback;
  return ["1", "true", "yes", "on"].includes(String(value).trim().toLowerCase());
}

function runtimeValue(key) {
  const runtime = typeof window !== "undefined" ? window.__TALENTSYNC_CONFIG__ : undefined;
  if (runtime && Object.prototype.hasOwnProperty.call(runtime, key)) {
    const value = runtime[key];
    if (value != null && value !== "") return value;
  }
  return import.meta.env[key];
}

export const showEmployeeDashboard = envFlag(runtimeValue("VITE_SHOW_EMPLOYEE_DASHBOARD"), true);
export const showQuickDemo = envFlag(runtimeValue("VITE_SHOW_QUICK_DEMO"), true);
export const showPricingContactOverlay = envFlag(runtimeValue("VITE_SHOW_PRICING_CONTACT_OVERLAY"), true);
export const pricingContactEmail = String(runtimeValue("VITE_PRICING_CONTACT_EMAIL") || "hello@talentsync.com").trim();

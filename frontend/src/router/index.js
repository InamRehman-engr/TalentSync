import { createRouter, createWebHistory } from "vue-router";
import LandingPage from "../views/LandingPage.vue";
import Dashboard from "../views/Dashboard.vue";
import FeaturesPage from "../views/FeaturesPage.vue";
import SolutionsPage from "../views/SolutionsPage.vue";
import PricingPage from "../views/PricingPage.vue";
import PricingContactPage from "../views/PricingContactPage.vue";
import AboutPage from "../views/AboutPage.vue";
import HiringGuidePage from "../views/HiringGuidePage.vue";
import DemoPage from "../views/DemoPage.vue";
import LoginPage from "../views/LoginPage.vue";
import TermsPage from "../views/TermsPage.vue";
import PrivacyPage from "../views/PrivacyPage.vue";
import EmployerDashboard from "../views/EmployerDashboard.vue";
import EmployeeDashboard from "../views/EmployeeDashboard.vue";
import {
  showEmployeeDashboard,
  showQuickDemo,
  showPricingContactOverlay,
  pricingContactEmail,
} from "../runtimeConfig.js";

export {
  showEmployeeDashboard,
  showQuickDemo,
  showPricingContactOverlay,
  pricingContactEmail,
};

const pricingRoute = showPricingContactOverlay
  ? { path: "/pricing", name: "Pricing", component: PricingContactPage }
  : { path: "/pricing", name: "Pricing", component: PricingPage };

const routes = [
  { path: "/", name: "Landing", component: LandingPage },
  { path: "/dashboard", name: "Dashboard", component: Dashboard },
  { path: "/features", name: "Features", component: FeaturesPage },
  { path: "/solutions", name: "Solutions", component: SolutionsPage },
  pricingRoute,
  { path: "/about", name: "About", component: AboutPage },
  { path: "/guide", name: "HiringGuide", component: HiringGuidePage },
  { path: "/resources", redirect: "/guide" },
  ...(showQuickDemo
    ? [{ path: "/demo", name: "Demo", component: DemoPage }]
    : [{ path: "/demo", redirect: "/" }]),
  { path: "/login", name: "Login", component: LoginPage },
  { path: "/terms", name: "Terms", component: TermsPage },
  { path: "/privacy", name: "Privacy", component: PrivacyPage },
  { path: "/employer", name: "Employer", component: EmployerDashboard, meta: { requiresAuth: true, role: "employer" } },
  ...(showEmployeeDashboard ? [{ path: "/employee", name: "Employee", component: EmployeeDashboard, meta: { requiresAuth: true, role: "employee" } }] : []),
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

router.beforeEach((to) => {
  if (!showQuickDemo && to.path === "/demo") {
    return { name: "Landing" };
  }

  if (!showEmployeeDashboard && to.path === "/employee") {
    return { name: "Landing" };
  }

  if (to.meta.requiresAuth) {
    const token = localStorage.getItem("ts_token");
    if (!token) return { name: "Login" };
  }
});

export default router;

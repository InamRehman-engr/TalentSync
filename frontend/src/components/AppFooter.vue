<script setup>
import { showQuickDemo } from "../router/index";
</script>

<template>
  <footer class="bg-footer text-neutral-400">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Top row — brand + columns -->
      <div class="py-12 sm:py-16 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-8 lg:gap-12">
        <!-- Brand column — spans 2 on lg -->
        <div class="col-span-2 sm:col-span-3 lg:col-span-2">
          <div class="flex items-center gap-2.5 mb-4">
            <img src="/favicon.svg" alt="TalentSync" class="w-8 h-8 rounded-lg" />
            <span class="text-lg font-bold text-white">TalentSync</span>
          </div>
          <p class="text-sm leading-relaxed max-w-xs mb-6">
            AI-powered recruitment platform that automates talent discovery, screening, and hiring workflows.
          </p>
          <div class="flex items-center gap-4">
            <a href="#" class="w-8 h-8 rounded-full bg-neutral-800 flex items-center justify-center hover:bg-neutral-700 transition-colors">
              <span class="text-xs text-neutral-300">X</span>
            </a>
            <a href="#" class="w-8 h-8 rounded-full bg-neutral-800 flex items-center justify-center hover:bg-neutral-700 transition-colors">
              <span class="text-xs text-neutral-300">in</span>
            </a>
            <a href="#" class="w-8 h-8 rounded-full bg-neutral-800 flex items-center justify-center hover:bg-neutral-700 transition-colors">
              <span class="text-xs text-neutral-300">GH</span>
            </a>
          </div>
        </div>

        <!-- Product -->
        <div>
          <h4 class="text-xs font-semibold text-neutral-200 uppercase tracking-wider mb-4">Product</h4>
          <ul class="space-y-3 text-sm">
            <li><router-link to="/features" class="hover:text-white transition-colors">Features</router-link></li>
            <li><router-link to="/pricing" class="hover:text-white transition-colors">Pricing</router-link></li>
            <li><router-link to="/solutions" class="hover:text-white transition-colors">Solutions</router-link></li>
            <li v-if="showQuickDemo"><router-link to="/demo" class="hover:text-white transition-colors">Book a Demo</router-link></li>
          </ul>
        </div>

        <!-- Company -->
        <div>
          <h4 class="text-xs font-semibold text-neutral-200 uppercase tracking-wider mb-4">Company</h4>
          <ul class="space-y-3 text-sm">
            <li><router-link to="/about" class="hover:text-white transition-colors">About Us</router-link></li>
            <li><router-link to="/guide" class="hover:text-white transition-colors">Hiring Guide</router-link></li>
          </ul>
        </div>

        <!-- Legal -->
        <div>
          <h4 class="text-xs font-semibold text-neutral-200 uppercase tracking-wider mb-4">Legal</h4>
          <ul class="space-y-3 text-sm">
            <li><router-link to="/privacy" class="hover:text-white transition-colors">Privacy Policy</router-link></li>
            <li><router-link to="/terms" class="hover:text-white transition-colors">Terms of Service</router-link></li>
          </ul>
        </div>
      </div>

      <!-- Bottom bar -->
      <div class="py-6 border-t border-neutral-800/60 flex flex-col sm:flex-row items-center justify-between gap-3">
        <p class="text-xs text-neutral-500">&copy; 2026 TalentSync. All rights reserved.</p>
        <p class="text-xs text-neutral-600">Built with ❤️ in Islamabad</p>
      </div>
    </div>
  </footer>
</template>

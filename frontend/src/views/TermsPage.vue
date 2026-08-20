<script setup>
import Navbar from "../components/Navbar.vue";
import AppFooter from "../components/AppFooter.vue";
</script>

<template>
  <div class="min-h-screen bg-white">
    <Navbar />

    <article class="max-w-3xl mx-auto px-6 lg:px-8 py-20">
      <h1 class="text-3xl font-bold text-neutral-900 mb-2">Terms of Service</h1>
      <p class="text-sm text-neutral-400 mb-10">Last updated: April 13, 2026</p>

      <div class="prose prose-slate prose-sm max-w-none space-y-8">
        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">1. Acceptance of Terms</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            By accessing or using TalentSync ("the Platform"), you agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, you may not access or use the Platform. These Terms apply to all users, including employers, employees, and visitors.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">2. Description of Service</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            TalentSync is an AI-powered recruitment platform that connects employers with candidates through automated screening, scoring, and pipeline management. The Platform provides job posting, candidate discovery, ATS scoring, and workflow automation tools.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">3. User Accounts</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            You must register for an account to access certain features. You are responsible for maintaining the confidentiality of your login credentials and for all activities that occur under your account. You agree to provide accurate, current, and complete information during registration.
          </p>
          <ul class="mt-3 space-y-2 text-sm text-neutral-600">
            <li class="flex items-start gap-2"><span class="text-primary-600 mt-1">•</span> <span><strong>Employers</strong> may post jobs, search candidates, and manage hiring pipelines.</span></li>
            <li class="flex items-start gap-2"><span class="text-primary-600 mt-1">•</span> <span><strong>Employees</strong> may create profiles, apply for jobs, and view ATS feedback.</span></li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">4. Acceptable Use</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">You agree not to:</p>
          <ul class="mt-3 space-y-2 text-sm text-neutral-600">
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> Use the Platform for any unlawful purpose or in violation of any applicable laws.</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> Post false, misleading, or discriminatory job listings or profile information.</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> Attempt to gain unauthorized access to other users' accounts or Platform systems.</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> Scrape, crawl, or harvest data from the Platform without express permission.</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> Upload malicious code, viruses, or content that could harm the Platform.</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">5. Intellectual Property</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            All content, features, and functionality of the Platform — including but not limited to text, graphics, logos, icons, algorithms, and software — are owned by TalentSync and protected by intellectual property laws. You may not reproduce, distribute, or create derivative works without our prior written consent.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">6. AI & Automated Scoring</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            TalentSync uses AI-based algorithms to score and rank candidates. These scores are advisory only and should not be the sole basis for hiring decisions. Employers are responsible for making independent, fair, and legal hiring decisions. We continuously work to minimize bias in our algorithms.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">7. Payment & Billing</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            Paid features are billed on a per-user, per-month basis. You may cancel at any time and retain access until the end of your billing cycle. Refunds are handled on a case-by-case basis. All prices are in USD unless stated otherwise.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">8. Limitation of Liability</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            To the maximum extent permitted by law, TalentSync shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising out of your use of the Platform. Our total liability shall not exceed the amount you paid to TalentSync in the twelve (12) months preceding the claim.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">9. Termination</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            We reserve the right to suspend or terminate your account at any time for violations of these Terms or for any other reason at our sole discretion. Upon termination, your right to use the Platform ceases immediately. You may export your data before termination by contacting support.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">10. Changes to Terms</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            We may update these Terms from time to time. We will notify you of any material changes by posting the new Terms on this page and updating the "Last updated" date. Your continued use of the Platform after any changes constitutes acceptance of the new Terms.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">11. Contact Us</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            If you have any questions about these Terms, please contact us at
            <a href="mailto:legal@talentsync.com" class="text-primary-600 hover:text-primary-800 font-medium">legal@talentsync.com</a>.
          </p>
        </section>
      </div>
    </article>

    <AppFooter />
  </div>
</template>

<script setup>
import Navbar from "../components/Navbar.vue";
import AppFooter from "../components/AppFooter.vue";
</script>

<template>
  <div class="min-h-screen bg-white">
    <Navbar />

    <article class="max-w-3xl mx-auto px-6 lg:px-8 py-20">
      <h1 class="text-3xl font-bold text-neutral-900 mb-2">Privacy Policy</h1>
      <p class="text-sm text-neutral-400 mb-10">Last updated: April 13, 2026</p>

      <div class="prose prose-slate prose-sm max-w-none space-y-8">
        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">1. Introduction</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            TalentSync ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our platform. Please read this policy carefully.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">2. Information We Collect</h2>
          <p class="text-sm text-neutral-600 leading-relaxed mb-3">We collect information you provide directly to us:</p>
          <ul class="space-y-2 text-sm text-neutral-600">
            <li class="flex items-start gap-2"><span class="text-primary-600 mt-1">•</span> <span><strong>Account Information:</strong> Name, email address, password, role (employer/employee), company name, and job title.</span></li>
            <li class="flex items-start gap-2"><span class="text-primary-600 mt-1">•</span> <span><strong>Profile Data:</strong> Resume content, skills, work experience, education, and location.</span></li>
            <li class="flex items-start gap-2"><span class="text-primary-600 mt-1">•</span> <span><strong>Job Data:</strong> Job descriptions, requirements, and candidate search queries (for employers).</span></li>
            <li class="flex items-start gap-2"><span class="text-primary-600 mt-1">•</span> <span><strong>Application Data:</strong> Resume submissions, ATS scores, and application status history.</span></li>
            <li class="flex items-start gap-2"><span class="text-primary-600 mt-1">•</span> <span><strong>Usage Data:</strong> Pages visited, features used, timestamps, and device information.</span></li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">3. How We Use Your Information</h2>
          <ul class="space-y-2 text-sm text-neutral-600">
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> To provide, maintain, and improve the Platform and its features.</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> To match candidates with job postings using AI-based scoring algorithms.</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> To generate ATS compatibility scores for job applications.</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> To communicate with you about your account, updates, and support requests.</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> To analyze usage patterns and improve our AI models (in aggregated, anonymized form).</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> To comply with legal obligations and enforce our Terms of Service.</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">4. AI & Automated Processing</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            TalentSync uses AI algorithms to process resumes, score candidates, and rank applicants. This automated processing is used to assist — not replace — human hiring decisions. We are committed to fairness, transparency, and minimizing bias in our AI systems. You may request a human review of any AI-generated score by contacting support.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">5. Data Sharing & Disclosure</h2>
          <p class="text-sm text-neutral-600 leading-relaxed mb-3">We do not sell your personal data. We may share information in the following circumstances:</p>
          <ul class="space-y-2 text-sm text-neutral-600">
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> <strong>With employers:</strong> When you apply for a job, your profile and resume are shared with the posting employer.</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> <strong>Service providers:</strong> We work with third-party services for hosting, analytics, and email delivery.</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> <strong>Legal requirements:</strong> When required by law, regulation, or legal process.</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> <strong>Business transfers:</strong> In connection with a merger, acquisition, or sale of assets.</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">6. Data Security</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            We implement industry-standard security measures including encryption at rest and in transit, access controls, and regular security audits. However, no method of transmission or storage is 100% secure. We cannot guarantee absolute security of your data.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">7. Data Retention</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            We retain your personal data for as long as your account is active or as needed to provide services. You may request deletion of your account and associated data at any time by contacting support. We will process deletion requests within 30 days, subject to legal retention requirements.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">8. Your Rights</h2>
          <p class="text-sm text-neutral-600 leading-relaxed mb-3">Depending on your jurisdiction, you may have the right to:</p>
          <ul class="space-y-2 text-sm text-neutral-600">
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> Access, update, or delete your personal information.</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> Export your data in a portable format.</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> Opt out of automated decision-making and profiling.</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> Withdraw consent for data processing at any time.</li>
            <li class="flex items-start gap-2"><span class="text-neutral-400 mt-1">•</span> Lodge a complaint with a supervisory authority.</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">9. Cookies & Tracking</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            We use essential cookies for authentication and session management. We do not use third-party advertising cookies. Analytics cookies are used only in aggregated, anonymized form to improve the Platform experience.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">10. Children's Privacy</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            TalentSync is not intended for users under the age of 16. We do not knowingly collect personal information from children. If you believe a child under 16 has provided us data, please contact us immediately.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">11. Changes to This Policy</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            We may update this Privacy Policy from time to time. We will notify you of material changes by posting the new policy on this page and updating the "Last updated" date. We encourage you to review this policy periodically.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-semibold text-neutral-900 mb-3">12. Contact Us</h2>
          <p class="text-sm text-neutral-600 leading-relaxed">
            For any questions regarding this Privacy Policy or your data, please contact us at
            <a href="mailto:privacy@talentsync.com" class="text-primary-600 hover:text-primary-800 font-medium">privacy@talentsync.com</a>.
          </p>
        </section>
      </div>
    </article>

    <AppFooter />
  </div>
</template>

// tf-frontend/app/terms/page.tsx

'use client';

import React from 'react';
import Navbar from '@/app/components/Navbar';
import Footer from '@/app/components/Footer';
import ScrollAnimation from '@/app/components/ScrollAnimation';

export default function TermsPage() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-[#b1c9a7] via-[#e9efe6] to-[#79a267]">
      <Navbar />
      
      {/* Main Content */}
      <main className="flex-grow pt-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <ScrollAnimation>
            <h1 className="text-4xl font-bold text-[#1c2617] mb-8">Terms and Conditions</h1>
            <p className="text-[#4a653e] mb-12">Last updated: January 13, 2025</p>
          </ScrollAnimation>

          <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg p-8 space-y-8">
            {/* Section 1: Introduction */}
            <ScrollAnimation>
              <section className="space-y-4">
                <h2 className="text-2xl font-semibold text-[#1c2617]">1. Introduction</h2>
                <p className="text-gray-700">
                  Welcome to TrainFair. These Terms and Conditions govern your use of TrainFair's platform 
                  and services. By using our platform, you agree to these terms in their entirety. If you 
                  disagree with any part of these terms, you may not use our services.
                </p>
              </section>
            </ScrollAnimation>

            {/* Section 2: Definitions */}
            <ScrollAnimation>
              <section className="space-y-4">
                <h2 className="text-2xl font-semibold text-[#1c2617]">2. Definitions</h2>
                <div className="space-y-2">
                  <p className="text-gray-700">
                    <span className="font-semibold">Platform:</span> The TrainFair website, APIs, and related services.
                  </p>
                  <p className="text-gray-700">
                    <span className="font-semibold">Publisher:</span> Content creators and owners who make their content 
                    available through our platform.
                  </p>
                  <p className="text-gray-700">
                    <span className="font-semibold">AI Company:</span> Organizations that access content through our 
                    platform for AI training or RAG purposes.
                  </p>
                </div>
              </section>
            </ScrollAnimation>

            {/* Section 3: Platform Usage */}
            <ScrollAnimation>
              <section className="space-y-4">
                <h2 className="text-2xl font-semibold text-[#1c2617]">3. Platform Usage</h2>
                <div className="space-y-4">
                  <h3 className="text-xl font-medium text-[#4a653e]">3.1 Publisher Terms</h3>
                  <p className="text-gray-700">
                    Publishers retain all rights to their content while granting AI Companies access through 
                    our platform. Publishers are responsible for ensuring they have the necessary rights to 
                    make their content available.
                  </p>
                  
                  <h3 className="text-xl font-medium text-[#4a653e]">3.2 AI Company Terms</h3>
                  <p className="text-gray-700">
                    AI Companies agree to access content only through our authorized APIs and to accurately 
                    report usage. They must implement our tracking system and not circumvent our detection 
                    mechanisms.
                  </p>
                </div>
              </section>
            </ScrollAnimation>

            {/* Section 4: Payments */}
            <ScrollAnimation>
              <section className="space-y-4">
                <h2 className="text-2xl font-semibold text-[#1c2617]">4. Payments and Fees</h2>
                <div className="space-y-2">
                  <p className="text-gray-700">
                    TrainFair charges a 3% platform fee on all transactions. Publishers set their own rates 
                    for content access. All payments are processed through our secure payment system.
                  </p>
                  <p className="text-gray-700">
                    Publisher payouts occur automatically when the account balance exceeds $100, or monthly 
                    if the balance exceeds $20.
                  </p>
                </div>
              </section>
            </ScrollAnimation>

            {/* Section 5: Data Privacy */}
            <ScrollAnimation>
              <section className="space-y-4">
                <h2 className="text-2xl font-semibold text-[#1c2617]">5. Data Privacy and Security</h2>
                <p className="text-gray-700">
                  We maintain industry-standard security practices to protect your data. Usage data is 
                  collected to facilitate transactions and improve our services. For complete details, 
                  please review our Privacy Policy.
                </p>
              </section>
            </ScrollAnimation>

            {/* Section 6: Termination */}
            <ScrollAnimation>
              <section className="space-y-4">
                <h2 className="text-2xl font-semibold text-[#1c2617]">6. Termination</h2>
                <p className="text-gray-700">
                  TrainFair reserves the right to terminate or suspend accounts that violate these terms 
                  or engage in fraudulent activity. Users may terminate their account at any time, subject 
                  to ongoing obligations.
                </p>
              </section>
            </ScrollAnimation>

            {/* Section 7: Liability */}
            <ScrollAnimation>
              <section className="space-y-4">
                <h2 className="text-2xl font-semibold text-[#1c2617]">7. Limitation of Liability</h2>
                <p className="text-gray-700">
                  TrainFair is not liable for any indirect, incidental, or consequential damages arising 
                  from platform use. Our total liability is limited to the amount paid to us over the 
                  previous 12 months.
                </p>
              </section>
            </ScrollAnimation>

            {/* Contact Section */}
            <ScrollAnimation>
              <section className="space-y-4 bg-[#e9efe6] p-6 rounded-lg mt-12">
                <h2 className="text-2xl font-semibold text-[#1c2617]">Questions?</h2>
                <p className="text-[#4a653e]">
                  If you have any questions about these Terms and Conditions, please contact us at{' '}
                  <a 
                    href="mailto:info@trainfair.io" 
                    className="text-[#4a653e] font-semibold hover:text-[#79a267] transition-colors"
                  >
                    info@trainfair.io
                  </a>
                </p>
              </section>
            </ScrollAnimation>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
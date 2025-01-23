// tf-frontend/app/privacy/page.tsx

'use client';

import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import ScrollAnimation from '../components/ScrollAnimation';

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#b1c9a7] via-[#e9efe6] to-[#79a267]">
      <Navbar />

      <main className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <ScrollAnimation>
            <h1 className="text-4xl font-bold text-[#1c2617] text-center mb-8">
              Privacy Policy
            </h1>
          </ScrollAnimation>

          <div className="space-y-8">
            {/* Introduction */}
            <ScrollAnimation>
              <section className="bg-white rounded-lg shadow-lg p-8">
                
                <h2 className="text-2xl font-semibold text-[#1c2617] mb-4">
                  Introduction
                </h2>
                <p className="text-gray-700 mb-4">
                  At TrainFair, we take your privacy seriously. This Privacy Policy explains how we collect, 
                  use, disclose, and safeguard your information when you use our platform. Please read this 
                  privacy policy carefully. If you do not agree with the terms of this privacy policy, please 
                  do not access the platform.
                </p>
                <p className="text-gray-700">
                  We reserve the right to make changes to this Privacy Policy at any time and for any reason
                  by posting a revised version on our website. 
                  You are encouraged to periodically review this privacy policy to stay informed of updates.
                </p>
              </section>
            </ScrollAnimation>

            {/* Information We Collect */}
            <ScrollAnimation>
              <section className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-semibold text-[#1c2617] mb-4">
                  Information We Collect
                </h2>
                <h3 className="text-xl font-medium text-[#1c2617] mb-3">Personal Data</h3>
                <p className="text-gray-700 mb-4">
                  Personally identifiable information that you may provide to us includes:
                </p>
                <ul className="list-disc list-inside text-gray-700 mb-6 space-y-2">
                  <li>Name and contact information</li>
                  <li>Email addresses</li>
                  <li>Business information</li>
                  <li>Payment information</li>
                  <li>Login credentials</li>
                </ul>

                <h3 className="text-xl font-medium text-[#1c2617] mb-3">Usage Data</h3>
                <p className="text-gray-700 mb-4">
                  We may also collect information about how you access and use the platform:
                </p>
                <ul className="list-disc list-inside text-gray-700 space-y-2">
                  <li>Access times and duration</li>
                  <li>Pages viewed</li>
                  <li>Links clicked</li>
                  <li>Technical data about your device and internet connection</li>
                </ul>
              </section>
            </ScrollAnimation>

            {/* How We Use Your Information */}
            <ScrollAnimation>
              <section className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-semibold text-[#1c2617] mb-4">
                  How We Use Your Information
                </h2>
                <p className="text-gray-700 mb-4">
                  We may use the information we collect for various purposes:
                </p>
                <ul className="list-disc list-inside text-gray-700 space-y-2">
                  <li>Provide, operate, and maintain our platform</li>
                  <li>Process transactions and send related information</li>
                  <li>Monitor and analyze usage patterns and trends</li>
                  <li>Improve our services and user experience</li>
                  <li>Communicate with you about updates, support, and promotions</li>
                  <li>Detect and prevent fraudulent or unauthorized activity</li>
                  <li>Comply with legal obligations</li>
                </ul>
              </section>
            </ScrollAnimation>

            {/* Information Sharing */}
            <ScrollAnimation>
              <section className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-semibold text-[#1c2617] mb-4">
                  Information Sharing
                </h2>
                <p className="text-gray-700 mb-4">
                  We may share your information with third parties in certain situations:
                </p>
                <ul className="list-disc list-inside text-gray-700 space-y-2 mb-4">
                  <li>With service providers who assist in operating our platform</li>
                  <li>To comply with legal obligations</li>
                  <li>To protect and defend our rights and property</li>
                  <li>With your consent or at your direction</li>
                </ul>
                <p className="text-gray-700">
                  We do not sell, rent, or trade your personal information to third parties for 
                  marketing purposes without your explicit consent.
                </p>
              </section>
            </ScrollAnimation>

            {/* Data Security */}
            <ScrollAnimation>
              <section className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-semibold text-[#1c2617] mb-4">
                  Data Security
                </h2>
                <p className="text-gray-700 mb-4">
                  We implement appropriate technical and organizational security measures to protect 
                  your personal information from unauthorized access, disclosure, alteration, or 
                  destruction. However, no method of transmission over the internet is 100% secure, 
                  and we cannot guarantee absolute security.
                </p>
              </section>
            </ScrollAnimation>

            {/* Your Rights */}
            <ScrollAnimation>
              <section className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-semibold text-[#1c2617] mb-4">
                  Your Rights
                </h2>
                <p className="text-gray-700 mb-4">
                  You have certain rights regarding your personal information:
                </p>
                <ul className="list-disc list-inside text-gray-700 space-y-2">
                  <li>Access your personal information</li>
                  <li>Correct inaccurate or incomplete information</li>
                  <li>Request deletion of your information</li>
                  <li>Object to or restrict processing of your information</li>
                  <li>Request transfer of your information</li>
                  <li>Withdraw consent where applicable</li>
                </ul>
              </section>
            </ScrollAnimation>

            {/* Contact Information */}
            <ScrollAnimation>
              <section className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-semibold text-[#1c2617] mb-4">
                  Contact Us
                </h2>
                <p className="text-gray-700">
                  If you have any questions about this Privacy Policy or our practices, please contact us at:{' '}
                  <a href="mailto:info@trainfair.io" className="text-[#4a653e] hover:text-[#79a267] transition-colors">
                    info@trainfair.io
                  </a>
                </p>
              </section>
            </ScrollAnimation>
            
            {/* Last Updated */}
            <ScrollAnimation>
              <p className="text-center text-gray-600 mt-8">
                Last updated: January 13, 2025
              </p>
            </ScrollAnimation>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
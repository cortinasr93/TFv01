// tf-frontend/app/register/page.tsx

'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Newspaper } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import ScrollAnimation from '../components/ScrollAnimation';

export default function RegistrationSelection() {
  const router = useRouter();

  // Use Next.js router instead of window.location
  const handleNavigation = (path: string) => {
    router.push(path);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#b1c9a7] via-[#e9efe6] to-[#79a267]">
      <Navbar />

      <div className="flex flex-col justify-center py-24 px-4 sm:px-6 lg:px-8">
        <ScrollAnimation>
          <div className="sm:mx-auto sm:w-full sm:max-w-md">
            <h1 className="text-center text-4xl font-bold text-[#1c2617] tracking-tight">
              Join TrainFair
            </h1>
            <p className="mt-3 text-center text-lg text-[#4a653e]">
              Choose your role in the future of AI training
            </p>
          </div>
        </ScrollAnimation>

        <ScrollAnimation className="mt-12 sm:mx-auto sm:w-full sm:max-w-2xl">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            {/* Publisher Card */}
            <div 
              onClick={() => handleNavigation('/register/publisher')}
              className="relative group overflow-hidden bg-white rounded-xl shadow-sm border border-gray-200 hover:border-[#4a653e] hover:shadow-md transition-all duration-300 cursor-pointer"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-[#e9efe6] to-[#e9efe6]/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative p-8">
                <div className="w-12 h-12 rounded-lg bg-[#e9efe6] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Newspaper className="w-6 h-6 text-[#4a653e]" />
                </div>
                <h3 className="text-xl font-semibold text-[#1c2617] mb-2">Publisher</h3>
                <p className="text-[#4a653e] mb-6">
                  Monetize your content and contribute to the advancement of AI while maintaining control over your data.
                </p>
                <div className="flex items-center text-[#4a653e] font-medium">
                  Get started
                  <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>

            {/* AI Company Card */}
            <div 
              onClick={() => handleNavigation('/register/ai-company')}
              className="relative group overflow-hidden bg-white rounded-xl shadow-sm border border-gray-200 hover:border-[#4a653e] hover:shadow-md transition-all duration-300 cursor-pointer"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-[#e9efe6] to-[#e9efe6]/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative p-8">
                <div className="w-12 h-12 rounded-lg bg-[#e9efe6] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-6 h-6 text-[#4a653e]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-[#1c2617] mb-2">AI Company</h3>
                <p className="text-[#4a653e] mb-6">
                  Access high-quality training data through our streamlined marketplace with transparent pricing.
                </p>
                <div className="flex items-center text-[#4a653e] font-medium">
                  Get started
                  <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-12 text-center text-sm text-[#4a653e]">
            Already have an account?{' '}
            <Link 
              href="/login"
              className="text-[#4a653e] hover:text-[#79a267] font-medium transition-colors"
            >
              Sign in
            </Link>
          </div>
        </ScrollAnimation>
      </div>

      <Footer />
    </div>
  );
}
import React from 'react';

export default function RegistrationSelection() {
  // Replace React Router navigation with simple URL navigation
  const handleNavigation = (path) => {
    window.location.href = path;
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Navigation Bar */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-sm border-b border-gray-100 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="text-xl font-semibold text-gray-900">
              TrainFair
            </div>
            <div className="text-sm">
              <a 
                href="/login"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                Sign in
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex flex-col justify-center py-24 px-4 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <h1 className="text-center text-4xl font-bold text-gray-900 tracking-tight">
            Join TrainFair
          </h1>
          <p className="mt-3 text-center text-lg text-gray-600">
            Choose your role in the future of AI training
          </p>
        </div>

        <div className="mt-12 sm:mx-auto sm:w-full sm:max-w-2xl">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            {/* Publisher Card */}
            <div 
              onClick={() => handleNavigation('/register/publisher')}
              className="relative group overflow-hidden bg-white rounded-xl shadow-sm border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all duration-300 cursor-pointer"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-50 to-blue-100/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative p-8">
                <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-6 h-6 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9.5a2.5 2.5 0 00-2.5-2.5H15" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Publisher</h3>
                <p className="text-gray-600 mb-6">
                  Monetize your content and contribute to the advancement of AI while maintaining control over your data.
                </p>
                <div className="flex items-center text-blue-600 font-medium">
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
              className="relative group overflow-hidden bg-white rounded-xl shadow-sm border border-gray-200 hover:border-purple-400 hover:shadow-md transition-all duration-300 cursor-pointer"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-purple-50 to-purple-100/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative p-8">
                <div className="w-12 h-12 rounded-lg bg-purple-50 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-6 h-6 text-purple-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">AI Company</h3>
                <p className="text-gray-600 mb-6">
                  Access high-quality training data through our streamlined marketplace with transparent pricing.
                </p>
                <div className="flex items-center text-purple-600 font-medium">
                  Get started
                  <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-12 text-center text-sm text-gray-500">
            Already have an account?{' '}
            <a 
              href="/login"
              className="text-blue-600 hover:text-blue-800 font-medium transition-colors"
            >
              Sign in
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
'use client';

import React, { useState, useEffect } from 'react';

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 10);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav
      className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        isScrolled ? 'bg-white/90 shadow backdrop-blur-sm' : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <span
            className={`text-2xl font-bold ${
              isScrolled ? 'text-gray-900' : 'text-white'
            }`}
          >
            TrainFair
          </span>
          <div className="flex items-center gap-8">
            <a
              href="#features"
              className={`hover:text-gray-300 transition-colors ${
                isScrolled ? 'text-gray-600' : 'text-white'
              }`}
            >
              Features
            </a>
            <a
              href="#pricing"
              className={`hover:text-gray-300 transition-colors ${
                isScrolled ? 'text-gray-600' : 'text-white'
              }`}
            >
              Pricing
            </a>
            <div className="flex gap-4">
              <a
                href="/login"
                className={`px-4 py-2 rounded-lg border border-transparent ${
                    isScrolled 
                        ? 'hover:border-[#4a653e] hover:[#4a653e]' 
                        : 'hover:border-white hover:text-white'
                }transition-colors`}
              >
                Log in
              </a>
              <a
                href="/register"
                className="px-4 py-2 rounded-lg bg-[#4a653e] text-white hover:bg-white hover:text-[#4a653e] transition-colors"
              >
                Sign up
              </a>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

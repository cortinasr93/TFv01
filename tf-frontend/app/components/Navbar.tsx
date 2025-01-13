'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const router = useRouter();
  const pathname = usePathname();
  const isHomePage = pathname === '/';

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 10);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleNavigation = (sectionId: string) => {
    if (isHomePage) {
      // if we're on the home page, just scroll to section
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    } else {
      // if we're on another page, navigate to home page with the section hash
      router.push(`/?section=${sectionId}`);
    }
  };

  // Effect to handle scroll after navigation from another page
  useEffect(() => {
    if (isHomePage) {
      const urlParams = new URLSearchParams(window.location.search);
      const section = urlParams.get('section');
      if (section) {
        const element = document.getElementById(section);
        if (element) {
          // Small delay to ensure page is fully loaded
          setTimeout(() => {
            element.scrollIntoView({ behavior: 'smooth' });

            // Clean up the URL
            window.history.replaceState({}, '', '/');
          }, 100);
        }
      }
    }
  }, [isHomePage]);

  return (
    <nav
      className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        isScrolled ? 'bg-white/90 shadow backdrop-blur-sm' : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link 
            href="/" 
            className={`text-2xl font-bold ${isScrolled ? 'text-gray-900' : 'text-white'} hover:opacity-80 transition-opacity`}
          >
            TrainFair
          </Link>
          
          <div className="flex items-center gap-8">
            <button
              onClick={() => handleNavigation('features')}
              className={`hover:text-gray-300 transition-colors ${
                isScrolled ? 'text-gray-600' : 'text-white'
              }`}
            >
              Features
            </button>
            <button
              onClick={() => handleNavigation('pricing')}
              className={`hover:text-gray-300 transition-colors ${
                isScrolled ? 'text-gray-600' : 'text-white'
              }`}
            >
              Pricing
            </button>
            <div className="flex gap-4">
              <Link
                href="/login"
                className={`px-4 py-2 rounded-lg border border-transparent ${
                  isScrolled 
                    ? 'hover:border-[#4a653e] hover:text-[#4a653e]' 
                    : 'hover:border-white hover:text-white'
                } transition-colors`}
              >
                Log in
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 rounded-lg bg-[#4a653e] text-white hover:bg-white hover:text-[#4a653e] transition-colors"
              >
                Sign up
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

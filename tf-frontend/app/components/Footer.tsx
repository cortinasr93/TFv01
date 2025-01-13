'use client';

import React from 'react';
import Link from 'next/link';

const Footer = () => (
  <footer className="bg-[#1c2617] text-gray-400 py-12 px-4 sm:px-6 lg:px-8">
    <div className="max-w-7xl mx-auto">
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between">
        {/* Navigation Links */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-8 lg:flex-1">
          <div>
            <h3 className="text-white font-semibold mb-4">Product</h3>
            <ul className="space-y-2">
              <li>
                <Link 
                  href="/#features" 
                  className="hover:text-white transition-colors"
                >
                  Features
                </Link>
              </li>
              <li>
                <Link 
                  href="/#pricing" 
                  className="hover:text-white transition-colors"
                >
                  Pricing
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-white font-semibold mb-4">Resources</h3>
            <ul className="space-y-2">
              <li>
                <Link 
                  href="/contact" 
                  className="hover:text-white transition-colors"
                >
                  Support
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-white font-semibold mb-4">Legal</h3>
            <ul className="space-y-2">
              <li>
                <Link 
                  href="/privacy" 
                  className="hover:text-white transition-colors"
                >
                  Privacy
                </Link>
              </li>
              <li>
                <Link 
                  href="/terms" 
                  className="hover:text-white transition-colors"
                >
                  Terms
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Brand Text */}
        <div className="mt-12 lg:mt-0 lg:ml-12">
          <h2 className="text-6xl font-bold text-white tracking-tight opacity-10 lg:opacity-20 transition-opacity hover:opacity-25 select-none">
            TrainFair
          </h2>
        </div>
      </div>

      <div className="mt-8 pt-8 border-t border-[#4a653e] text-center">
        <p>© {new Date().getFullYear()} TrainFair. All rights reserved.</p>
      </div>
    </div>
  </footer>
);

export default Footer;
'use client';

import React from 'react';

const Footer = () => (
  <footer className="bg-gray-900 text-gray-400 py-12 px-4 sm:px-6 lg:px-8">
    <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
      <div>
        <h3 className="text-white font-semibold mb-4">Product</h3>
        <ul className="space-y-2">
          <li>
            <a href="#" className="hover:text-white transition-colors">
              Features
            </a>
          </li>
          <li>
            <a href="#" className="hover:text-white transition-colors">
              Pricing
            </a>
          </li>
          
        </ul>
      </div>
      <div>
        <h3 className="text-white font-semibold mb-4">Company</h3>
        <ul className="space-y-2">
          <li>
            <a href="#" className="hover:text-white transition-colors">
              About
            </a>
          </li>

        </ul>
      </div>
      <div>
        <h3 className="text-white font-semibold mb-4">Resources</h3>
        <ul className="space-y-2">

          <li>
            <a href="#" className="hover:text-white transition-colors">
              Support
            </a>
          </li>
        </ul>
      </div>
      <div>
        <h3 className="text-white font-semibold mb-4">Legal</h3>
        <ul className="space-y-2">
          <li>
            <a href="#" className="hover:text-white transition-colors">
              Privacy
            </a>
          </li>
          <li>
            <a href="#" className="hover:text-white transition-colors">
              Terms
            </a>
          </li>
        </ul>
      </div>
    </div>
    <div className="max-w-7xl mx-auto mt-8 pt-8 border-t border-gray-800 text-center">
      <p>© {new Date().getFullYear()} TrainFair. All rights reserved.</p>
    </div>
  </footer>
);

export default Footer;

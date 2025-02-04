// tf-frontend/app/components/PricingCard.tsx

'use client';

import React from 'react';
import { LucideIcon } from 'lucide-react';

interface PricingCardProps {
  title: string;
  icon: LucideIcon;
  features: string[];
  // ctaText: string;
  // ctaHref: string;
  // userType: 'publisher' | 'ai-company';
}

const PricingCard = ({
  title,
  icon: Icon,
  features,
  // ctaText,
  // ctaHref,
  // userType,
}: PricingCardProps) => (
  <div className="bg-white rounded-xl p-8 shadow-lg transform hover:scale-105 transition-transform duration-300 h-[420px] flex flex-col justify-between">
    <div className="flex items-center justify-center w-16 h-16 mx-auto mb-6 rounded-full bg-[#e9efe6]">
      <Icon className="w-8 h-8 text-[#4a653e]" />
    </div>
    
    <h3 className="text-2xl font-bold text-[#1c2617] mb-8">{title}</h3>
    
    <ul className="space-y-3 text-left mb-8">
      {features.map((feature, index) => (
        <li key={index} className="flex items-center">
          <svg
            className="w-5 h-5 text-green-500 mr-2 flex-shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M5 13l4 4L19 7"
            />
          </svg>
          <span>{feature}</span>
        </li>
      ))}
    </ul>
    
    {/* <a
      href={ctaHref}
      className="block w-full py-3 px-4 rounded-lg bg-[#4a653e] text-white hover:bg-[#79a267] transition-colors text-center font-medium mt-auto"
    >
      {ctaText}
    </a> */}
  </div>
);

export default PricingCard;
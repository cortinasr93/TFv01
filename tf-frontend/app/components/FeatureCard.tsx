'use client';

import React from 'react';

interface FeatureCardProps {
  icon: React.ElementType;
  title: string;
  description: string;
  color: string; // Add a color prop
}

const FeatureCard = ({ icon: Icon, title, description, color }: FeatureCardProps) => (
  <div className="group p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100">
    <div
      className="w-12 h-12 rounded-lg flex items-center justify-center mb-4"
      style={{ backgroundColor: `${color}33` }} // Add semi-transparent background color
    >
      <Icon className="w-6 h-6" color={color} /> {/* Pass icon color */}
    </div>
    <h3 className="text-xl font-semibold mb-2">{title}</h3>
    <p className="text-gray-600">{description}</p>
  </div>
);

export default FeatureCard;

'use client';

import React from 'react';
import { 
  Shield, Database, BarChart2, Newspaper, DollarSign, Bot, 
  Server, Lock, Zap, FileText, Award, Search, Cpu 
} from 'lucide-react';
import Navbar from './components/Navbar';
import ScrollAnimation from './components/ScrollAnimation';
import FeatureCard from './components/FeatureCard';
import PricingCard from './components/PricingCard';
import Footer from './components/Footer';

const DecorativeBackground = () => (
  <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-0 animate-fadeIn">
    <div className="absolute -top-1/2 -right-1/2 w-full h-full">
      <div className="w-[800px] h-[800px] rounded-full bg-gradient-to-br from-[#4a653e]/10 to-transparent blur-3xl" />
    </div>
    <div className="absolute -bottom-1/2 -left-1/2 w-full h-full">
      <div className="w-[600px] h-[600px] rounded-full bg-gradient-to-tr from-[#79a267]/10 to-transparent blur-3xl" />
    </div>
  </div>
);

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#b1c9a7] via-[#e9efe6] to-[#79a267] relative">
      <Navbar />
      <DecorativeBackground />

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 relative">
        <div className="max-w-7xl mx-auto text-center">
        <ScrollAnimation>
          <h1 className="text-5xl md:text-7xl font-bold text-[#1c2617] mb-8">
            Monetization in the
            <br />
            <span className="bg-gradient-to-r from-[#4a653e] to-[#79a267] text-transparent bg-clip-text">
               New Content Economy
            </span>
          </h1>
        </ScrollAnimation>

        <ScrollAnimation className="delay-300">
            <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-12">
              <div className="text-left">
                <h2 className="text-xl font-semibold text-[#1c2617] mb-3">Publishers</h2>
                <p className="text-lg text-[#4a653e]">
                  As AI-enhanced search transforms how people find information, your 
                  traffic—and ad revenue—are at risk. Get paid directly when AI companies 
                  use your content, creating a sustainable revenue stream for the AI era.
                </p>
              </div>
              <div className="text-left">
                <h2 className="text-xl font-semibold text-[#1c2617] mb-3">AI Companies</h2>
                <p className="text-lg text-[#4a653e]">
                Unlock high-quality training data and search-ready content from verified publishers 
                through our streamlined marketplace. TrainFair's transparent pricing, seamless 
                integration, and automated compliance empowers you to power accurate, 
                ethical AI-driven search experiences.
                </p>
              </div>
            </div>
          </ScrollAnimation>
          
        <ScrollAnimation className="delay-500">
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/register"
              className="px-8 py-4 rounded-lg bg-[#e9efe6] text-[#1c2617] hover:bg-[#b1c9a7] transition-colors font-medium"
            >
              Get started
            </a>
            <a
              href="/contact"
              className="px-8 py-4 rounded-lg bg-[#4a653e] text-white hover:bg-[#79a267] transition-colors font-medium"
            >
              Contact us
            </a>
          </div>
        </ScrollAnimation>
      </div>
    </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-[#e9efe6] relative">
        <div className="max-w-7xl mx-auto">
        <ScrollAnimation>
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-[#1c2617]">Why Choose TrainFair?</h2>
            <p className="text-xl text-[#4a653e]">
              The complete solution for both publishers and AI companies
            </p>
          </div>
        </ScrollAnimation>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* Publishers Column */}
            <div>
            <ScrollAnimation>
              <h3 className="text-2xl font-semibold mb-8 text-center text-[#1c2617]">
                Publishers
              </h3>
            </ScrollAnimation>

              <div className="space-y-6">
                {[
                  {
                    icon: DollarSign,
                    title: "Monetize Your Content",
                    description: "Automated payments for your content's use in AI training and RAG",
                    delay: "delay-100"
                  },
                  {
                    icon: Shield,
                    title: "Content Protection",
                    description: "Advanced bot detection and access controls to protect your data",
                    delay: "delay-200"
                  },
                  {
                    icon: BarChart2,
                    title: "Usage Analytics",
                    description: "Comprehensive dashboard showing how and when your content is used",
                    delay: "delay-300"
                  },
                  {
                    icon: Lock,
                    title: "Access Control",
                    description: "Full control over who can use your content",
                    delay: "delay-400"
                  }
                ].map((feature, index) => (
                  <ScrollAnimation key={index} className={feature.delay}>
                    <FeatureCard {...feature} color="#4a653e" />
                  </ScrollAnimation>
                ))}
              </div>
            </div>

            {/* AI Companies Column */}
            <div>
              <ScrollAnimation>
                <h3 className="text-2xl font-semibold mb-8 text-center text-[#1c2617]">
                  AI Companies
                </h3>
              </ScrollAnimation>
              
              <div className="space-y-6">
                {[
                  {
                    icon: Database,
                    title: "Quality Data Access",
                    description: "Access to verified, high-quality data from reputable publishers",
                    delay: "delay-100"
                  },
                  {
                    icon: Zap,
                    title: "Streamlined Integration",
                    description: "Simple API integration for both training and RAG workflows",
                    delay: "delay-200"
                  },
                  {
                    icon: FileText,
                    title: "Clear Licensing",
                    description: "Transparent usage rights and automated compliance tracking",
                    delay: "delay-300"
                  },
                  {
                    icon: Award,
                    title: "Cost Efficiency",
                    description: "Pay only for the content you use, with no hidden fees",
                    delay: "delay-400"
                  }
                ].map((feature, index) => (
                  <ScrollAnimation key={index} className={feature.delay}>
                    <FeatureCard {...feature} color="#4a653e" />
                  </ScrollAnimation>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-4 sm:px-6 lg:px-8 bg-[#4a653e] relative">
        <div className="max-w-7xl mx-auto text-center">
          <ScrollAnimation>
            <h2 className="text-4xl font-bold text-white mb-4">Simple, Fair Pricing</h2>
            <p className="text-xl text-[#e9efe6] mb-12">No upfront costs. Pay only for what you use.</p>
          </ScrollAnimation>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          <ScrollAnimation className="delay-100">
            <PricingCard
              title="Publishers"
              icon={Newspaper}
              features={[
                "Free to join",
                "Set your own content prices",
                "Only 3% transaction fee",
                "Automatic payouts",
              ]}
              ctaText="Start Earning"
              ctaHref="/register/publisher"
              userType="publisher"
            />
          </ScrollAnimation>
            
          <ScrollAnimation className="delay-200">
            <PricingCard
              title="AI Companies"
              icon={Cpu}
              features={[
                "Free to join",
                "Pay per token",
                "Simple API integration"
              ]}
              ctaText="Start Training"
              ctaHref="/register/ai-company"
              userType="ai-company"
            />
          </ScrollAnimation>
        </div>

        <ScrollAnimation className="delay-300">
          <p className="text-[#e9efe6] text-sm mt-8">
            Transparent pricing with no hidden fees. Publishers set their own rates.
          </p>
        </ScrollAnimation>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-[#e9efe6] relative">
      <ScrollAnimation>
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-4 text-[#1c2617]">Ready to Get Started?</h2>
          <p className="text-xl text-[#4a653e] mb-8">
            Join leading AI companies and publishers on TrainFair today
          </p>
          <div className="flex justify-center gap-4">
            <a
              href="/register"
              className="px-8 py-4 rounded-lg bg-[#4a653e] text-white hover:bg-[#79a267] transition-colors font-medium"
            >
              Create Your Account
            </a>
            <a
              href="/contact"
              className="px-8 py-4 rounded-lg border border-[#4a653e] text-[#1c2617] hover:bg-[#b1c9a7] transition-colors font-medium"
            >
              Contact Sales
            </a>
          </div>
        </div>
      </ScrollAnimation>
      </section>

      {/* Footer */}
      <Footer />
    </div>
  );
}

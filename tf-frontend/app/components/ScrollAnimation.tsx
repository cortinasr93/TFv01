// tf-frontend/app/components/ScrollAnimation.tsx

'use client';

import React, { useEffect, useRef } from 'react';

interface ScrollAnimationProps {
    children: React.ReactNode;
    className?: string;
}

const ScrollAnimation: React.FC<ScrollAnimationProps> = ({ children, className = "" }) => {
    const elementRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.remove('opacity-0', 'translate-y-8');
                        entry.target.classList.add('opacity-100', 'translate-y-0');                    }
                });
            },
            {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            }
        );

        if (elementRef.current) {
            observer.observe(elementRef.current);
        }

        return () => {
            if (elementRef.current) {
                observer.unobserve(elementRef.current);
            }
        };
    }, []);

    return (
        <div
            ref={elementRef}
            className={`opacity-0 translate-y-8 transition-all duration-700 ease-out ${className}`}
        >
            {children}
        </div>
    );
};

export default ScrollAnimation
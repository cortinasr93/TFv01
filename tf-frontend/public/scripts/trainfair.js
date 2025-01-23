// tf-frontend/public/scripts/trainfair.js

// Frontend code for Publisher websites
// Monitors bots for TF token; redirects them to TF if no token found

(function() {
    // Configuration object to store settings
    const config = {
        apiEndpoint: 'https://api.trainfair.com', // Replace with actual API endpoint
        tokenCacheTime: 300000, // Token cache duration (5 mins)
        defaultRedirectUrl: 'https://trainfair.io/register', // Default redirect for unauthorized access
        debugMode: true
    };

    // Cache object for storing validated tokens
    const tokenCache = new Map();

    // Utility functions
    const utils = {
        log: (...args) => {
            if (config.debugMode) {
                console.log('[TrainFair]:', ...args);
            }
        },

        // Check if request is likely from AI crawler
        isAICrawler: (userAgent) => {
            const aiPatterns = [
                'anthropic-ai',
                'claude-web',
                'chatgpt-user',
                'gptbot',
                'cohere-ai',
                'perplexitybot',
                'ccbot',
                'bytespider',
                'diffbot'
            ];
            return aiPatterns.some(pattern =>
                userAgent.toLowerCase().includes(pattern)
            );
        },

        // Extract token from various possible locations
        getToken: () => {

            // Check auhorization header if available
            const authHeader = document.querySelector('meta[name="tf-auth-token"]')?.content;
            if (authHeader) return authHeader;

            // Check URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const urlToken = urlParams.get('tf_token');
            if (urlToken) return urlToken;

            // Check cookies
            const cookies = document.cookie.split(';');
            const tokenCookie = cookies.find(c => c.trim().startsWith('tf_token='));
            return tokenCookie ? tokenCookie.split('=')[1].trim() : null;
        }
    };

    // Token validation
    class TokenValidator {
        constructor() {
            this.pendingValidations = new Map();
        }

        // Validate token with backend
        async validateToken(token) {
            // Check cache first
            if (tokenCache.has(token)) {
                const cachedResult = tokenCache.get(token);
                if (Date.now() < cachedResult.expiresAt) {
                    return cachedResult.isValid;
                }
                tokenCache.delete(token);
            }

            try {
                // Prevent duplicate validation requests
                if (this.pendingValidations.has(token)) {
                    return await this.pendingValidations.get(token);
                }

                const validationPromise = this._performValidation(token);
                this.pendingValidations.set(token, validationPromise);
                const isValid = await validationPromise;
                this.pendingValidations.delete(token);

                // Cache the result
                tokenCache.set(token, {
                    isValid,
                    expiresAt: Date.now() + config.tokenCacheTime
                });

                return isValid;
            } catch (error) {
                utils.log('Token validation error:', error);
                return false;
            }
        }

        async _performValidation(token) {
            try {
                const response = await fetch(`${config.apiEndpoint}/validate-token`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ token }) 
                });

                if (!response.ok) return false;
                const data = await response.json();
                return data.valid === true;
            } catch (error) {
                utils.log('API validation error:', error);
                return false
            }
        }
    }

    // Content protection manager
    class ContentProtector {
        constructor() {
            this.validator = new TokenValidator();
            this.protectedContent = new Set();
            this.initialized = false;
        }

        async init() {
            if (this.initialized) return;

            // Get protection settings from meta tags

            const settings = document.querySelector('meta[name="tf-settings"]')?.content;
            if (settings) {
                try {
                    Object.assign(config, JSON.parse(settings));
                } catch (e) {
                    utils.log('Error parsing settings:', e);
                }
            }

            // Initialize content protection
            this.setupProtection();
            this.initialized = true;
        }

        async setupProtection() {
            // Only apply protection for AI crawlers
            if (!utils.isAICrawler(navigator.userAgent)) {
                return;
            }

            const token = utils.getToken();
            if (!token) {
                this.handleUnauthorizedAccess();
                return;
            }

            const isValid = await this.validator.validateToken(token);
            if (!isValid) {
                this.handleUnauthorizedAccess();
                return;
            }

            utils.log('Valid token detected, allowig access');
        }

        handleUnauthorizedAccess() {
            // Get custom redirect URL if specified
            const redirectUrl = document.querySelector('meta[name="tf-redirect"]')?.content
                || config.defaultRedirectUrl;

            // Add publisher Id and return URL to redirect
            const currentUrl = encodeURIComponent(window.location.href);
            const publisherId = document.querySelector('meta[name="tf-publisher-id"]')?.content;

            const finalRedirect = new URL(redirectUrl);
            finalRedirect.searchParams.append('returnUrl', currentUrl);
            if (publisherId) {
                finalRedirect.searchParams.append('publisherId', publisherId);
            }

            // Redirect to TrainFair registration page
            window.location.href = finalRedirect.toString();            
        }
    }

    // Initialize protection when document is ready
    const protector = new ContentProtector();
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => protector.init());
    } else {
        protector.init();
    }
})();

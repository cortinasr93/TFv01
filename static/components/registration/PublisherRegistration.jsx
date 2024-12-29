
const { useState } = React;

function PublisherRegistration() {
  // Track current step
  const [step, setStep] = useState(1);

  // All form data in one state object
  const [formData, setFormData] = useState({
    // Step 1: Account Information
    name: '',
    email: '',
    password: '',
    confirmPassword: '',

    // Step 2: Publisher Details
    companyName: '',
    website: '',
    contentType: '',
    description: '',

    // Step 3: Content Details
    contentCategories: [],
    estimatedVolume: '',
    updateFrequency: '',

    // Contact Info (optional if you want to add more fields)
    phone: '',
    address: '',
    city: '',
    country: '',

    // Step 4: Terms
    acceptedTerms: false,
    acceptedPrivacy: false,
  });

  // Track errors & global loading status
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  // Generic handler for input changes
  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));

    // Clear any existing error for the field being changed
    if (errors[name]) {
      setErrors((prevErrs) => ({ ...prevErrs, [name]: '' }));
    }
  };

  // Simple validation per step
  const validateStep = (stepNumber) => {
    const newErrors = {};

    if (stepNumber === 1) {
      if (!formData.name) newErrors.name = 'Name is required';
      if (!formData.email) {
        newErrors.email = 'Email is required';
      } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
        newErrors.email = 'Please provide a valid email address';
      }

      if (!formData.password) {
        newErrors.password = 'Password is required';
      } else if (formData.password.length < 8) {
        newErrors.password = 'Password must be at least 8 characters';
      }

      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
    }

    if (stepNumber === 2) {
      if (!formData.companyName) newErrors.companyName = 'Company name is required';
      if (!formData.website) newErrors.website = 'Website is required';
      if (!formData.contentType) newErrors.contentType = 'Content type is required';
    }

    // Add or adjust validation for Step 3, Step 4, etc. if desired.
    // For example, require at least one content category, or that terms are checked, etc.

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Form submission handler
  const handleSubmit = (e) => {
    e.preventDefault();

    // Validate the current step
    if (!validateStep(step)) return;

    // If not on the last step, just move forward
    if (step < 4) {
      setStep(step + 1);
      return;
    }

    // Otherwise, do the final submission
    setLoading(true);
    // Typically you'd POST this data to your server here:
    setTimeout(() => {
      // Simulate successful submission
      setLoading(false);
      alert('Registration successful! (Form data logged to console)');
      console.log('Submitted formData:', formData);
    }, 1000);
  };

  // Render the step-specific fields
  const renderStepFields = () => {
    switch (step) {
      case 1:
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">1. Account Information</h2>

            {/* Name Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="name">
                Full Name
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className={`mt-1 block w-full border ${
                  errors.name ? 'border-red-500' : 'border-gray-300'
                } rounded-md p-2`}
              />
              {errors.name && <p className="text-red-600 text-sm">{errors.name}</p>}
            </div>

            {/* Email Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="email">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={`mt-1 block w-full border ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                } rounded-md p-2`}
              />
              {errors.email && <p className="text-red-600 text-sm">{errors.email}</p>}
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="password">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={`mt-1 block w-full border ${
                  errors.password ? 'border-red-500' : 'border-gray-300'
                } rounded-md p-2`}
              />
              {errors.password && <p className="text-red-600 text-sm">{errors.password}</p>}
            </div>

            {/* Confirm Password Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="confirmPassword">
                Confirm Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                className={`mt-1 block w-full border ${
                  errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
                } rounded-md p-2`}
              />
              {errors.confirmPassword && (
                <p className="text-red-600 text-sm">{errors.confirmPassword}</p>
              )}
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">2. Publisher Details</h2>

            {/* Company Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="companyName">
                Company/Organization Name
              </label>
              <input
                type="text"
                id="companyName"
                name="companyName"
                value={formData.companyName}
                onChange={handleChange}
                className={`mt-1 block w-full border ${
                  errors.companyName ? 'border-red-500' : 'border-gray-300'
                } rounded-md p-2`}
              />
              {errors.companyName && (
                <p className="text-red-600 text-sm">{errors.companyName}</p>
              )}
            </div>

            {/* Website URL */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="website">
                Website URL
              </label>
              <input
                type="url"
                id="website"
                name="website"
                value={formData.website}
                onChange={handleChange}
                className={`mt-1 block w-full border ${
                  errors.website ? 'border-red-500' : 'border-gray-300'
                } rounded-md p-2`}
                placeholder="https://..."
              />
              {errors.website && (
                <p className="text-red-600 text-sm">{errors.website}</p>
              )}
            </div>

            {/* Content Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="contentType">
                Primary Content Type
              </label>
              <select
                id="contentType"
                name="contentType"
                value={formData.contentType}
                onChange={handleChange}
                className={`mt-1 block w-full border ${
                  errors.contentType ? 'border-red-500' : 'border-gray-300'
                } rounded-md p-2`}
              >
                <option value="">-- Select --</option>
                <option value="news">News Articles</option>
                <option value="blog">Blog Posts</option>
                <option value="academic">Academic Papers</option>
                <option value="documentation">Technical Docs</option>
                <option value="other">Other</option>
              </select>
              {errors.contentType && (
                <p className="text-red-600 text-sm">{errors.contentType}</p>
              )}
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="description">
                Brief Description
              </label>
              <textarea
                id="description"
                name="description"
                rows="4"
                value={formData.description}
                onChange={handleChange}
                className="mt-1 block w-full border border-gray-300 rounded-md p-2"
                placeholder="Tell us about your content..."
              />
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">3. Content Details</h2>

            {/* Categories (checkbox group) */}
            <div>
              <p className="text-sm font-medium text-gray-700">Select your content categories:</p>
              <div className="mt-2 space-y-1">
                {[
                  'Technology',
                  'Science',
                  'Business',
                  'Health',
                  'Education',
                  'Arts',
                  'Entertainment',
                  'Other',
                ].map((cat) => (
                  <label key={cat} className="flex items-center text-sm">
                    <input
                      type="checkbox"
                      name="contentCategories"
                      value={cat}
                      checked={formData.contentCategories.includes(cat)}
                      onChange={(e) => {
                        const checked = e.target.checked;
                        setFormData((prev) => {
                          const currentCats = prev.contentCategories;
                          if (checked) {
                            return { ...prev, contentCategories: [...currentCats, cat] };
                          } else {
                            return {
                              ...prev,
                              contentCategories: currentCats.filter((c) => c !== cat),
                            };
                          }
                        });
                      }}
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded mr-2"
                    />
                    {cat}
                  </label>
                ))}
              </div>
            </div>

            {/* Estimated Volume */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="estimatedVolume">
                Estimated Monthly Content Volume
              </label>
              <select
                id="estimatedVolume"
                name="estimatedVolume"
                value={formData.estimatedVolume}
                onChange={handleChange}
                className="mt-1 block w-full border border-gray-300 rounded-md p-2"
              >
                <option value="">-- Select volume --</option>
                <option value="small">&lt; 100 articles/posts</option>
                <option value="medium">100-1000 articles/posts</option>
                <option value="large">1000+ articles/posts</option>
              </select>
            </div>

            {/* Update Frequency */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="updateFrequency">
                Content Update Frequency
              </label>
              <select
                id="updateFrequency"
                name="updateFrequency"
                value={formData.updateFrequency}
                onChange={handleChange}
                className="mt-1 block w-full border border-gray-300 rounded-md p-2"
              >
                <option value="">-- Select frequency --</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
              </select>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">4. Terms &amp; Conditions</h2>

            <div className="bg-gray-100 p-4 rounded-md text-sm text-gray-700">
              By registering, you agree to participate in our content marketplace
              and allow AI companies to use your content for training purposes
              under the specified terms and conditions.
            </div>

            {/* Terms Checkbox */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="acceptedTerms"
                name="acceptedTerms"
                checked={formData.acceptedTerms}
                onChange={handleChange}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded mr-2"
              />
              <label htmlFor="acceptedTerms" className="text-sm text-gray-700">
                I accept the <a href="#" className="text-blue-600 underline">Terms and Conditions</a>
              </label>
            </div>

            {/* Privacy Checkbox */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="acceptedPrivacy"
                name="acceptedPrivacy"
                checked={formData.acceptedPrivacy}
                onChange={handleChange}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded mr-2"
              />
              <label htmlFor="acceptedPrivacy" className="text-sm text-gray-700">
                I accept the <a href="#" className="text-blue-600 underline">Privacy Policy</a>
              </label>
            </div>
          </div>
        );

      default:
        return <p>Unknown step.</p>;
    }
  };

  return (
    <div className="bg-white rounded-md shadow p-6">
      {/* Progress Indicator */}
      <div className="flex items-center justify-between mb-6">
        {[1, 2, 3, 4].map((num) => (
          <div key={num} className="flex items-center flex-1">
            <div
              className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-sm font-semibold
                ${step >= num ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-300 text-gray-600'}
              `}
            >
              {num}
            </div>
            {num !== 4 && (
              <div
                className={`flex-1 h-0.5 mx-2 ${
                  step > num ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        {/* Step-Specific Fields */}
        {renderStepFields()}

        {/* Error from final submission, if any */}
        {errors.submit && (
          <div className="mt-4 p-2 bg-red-100 text-red-700 border border-red-300 rounded">
            {errors.submit}
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="mt-6 flex justify-between">
          {step > 1 ? (
            <button
              type="button"
              className="px-4 py-2 border border-gray-300 rounded-md bg-white text-gray-700 hover:bg-gray-50"
              onClick={() => setStep(step - 1)}
            >
              Back
            </button>
          ) : (
            <div />
          )}
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            {loading
              ? 'Processing...'
              : step === 4
              ? 'Complete Registration'
              : 'Continue'}
          </button>
        </div>
      </form>
    </div>
  );
}


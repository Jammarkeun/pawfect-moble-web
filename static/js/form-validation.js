/**
 * PAWFECT FINDS - REAL-TIME FORM VALIDATION
 * Provides instant feedback on form inputs with visual indicators
 */

(function() {
    'use strict';

    // Validation rules
    const RULES = {
        email: {
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: 'Please enter a valid email address'
        },
        password: {
            minLength: 8,
            pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
            message: 'Password must be at least 8 characters with uppercase, lowercase, and number'
        },
        phone: {
            pattern: /^[\d\s\-\+\(\)]+$/,
            minLength: 10,
            message: 'Please enter a valid phone number'
        },
        required: {
            message: 'This field is required'
        },
        username: {
            pattern: /^[a-zA-Z0-9_]{3,20}$/,
            message: 'Username must be 3-20 characters (letters, numbers, underscore only)'
        },
        zipcode: {
            pattern: /^\d{4,10}$/,
            message: 'Please enter a valid postal/zip code'
        }
    };

    /**
     * Initialize form validation
     */
    function init() {
        // Find all forms with validation
        const forms = document.querySelectorAll('form[data-validate], form.needs-validation');
        
        forms.forEach(form => {
            setupFormValidation(form);
        });

        // Also setup validation for forms without explicit attribute
        setupCommonForms();
    }

    /**
     * Setup validation for common forms
     */
    function setupCommonForms() {
        // Login/Signup forms
        const authForms = document.querySelectorAll('form[action*="login"], form[action*="signup"], form[action*="register"]');
        authForms.forEach(form => setupFormValidation(form));

        // Checkout form
        const checkoutForm = document.querySelector('form[action*="checkout"]');
        if (checkoutForm) setupFormValidation(checkoutForm);

        // Settings/Profile forms
        const settingsForms = document.querySelectorAll('form[action*="settings"], form[action*="profile"]');
        settingsForms.forEach(form => setupFormValidation(form));
    }

    /**
     * Setup validation for a single form
     */
    function setupFormValidation(form) {
        if (form.dataset.validationSetup) return; // Already setup
        form.dataset.validationSetup = 'true';

        const inputs = form.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], input[type="tel"], input[type="number"], textarea, select');

        inputs.forEach(input => {
            // Add validation on blur
            input.addEventListener('blur', () => validateInput(input));

            // Add validation on input (with debounce)
            let inputTimeout;
            input.addEventListener('input', () => {
                clearTimeout(inputTimeout);
                inputTimeout = setTimeout(() => validateInput(input), 500);
            });

            // Add real-time feedback container
            addFeedbackContainer(input);
        });

        // Validate on submit
        form.addEventListener('submit', (e) => {
            let isValid = true;

            inputs.forEach(input => {
                if (!validateInput(input)) {
                    isValid = false;
                }
            });

            if (!isValid) {
                e.preventDefault();
                
                // Focus first invalid field
                const firstInvalid = form.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }

                // Show error message
                showFormError(form, 'Please fix the errors below before submitting.');
            }
        });

        // Password confirmation matching
        const password = form.querySelector('input[type="password"][name*="password"]:not([name*="confirm"])');
        const confirmPassword = form.querySelector('input[type="password"][name*="confirm"]');

        if (password && confirmPassword) {
            confirmPassword.addEventListener('input', () => {
                if (confirmPassword.value) {
                    validatePasswordMatch(password, confirmPassword);
                }
            });

            password.addEventListener('input', () => {
                if (confirmPassword.value) {
                    validatePasswordMatch(password, confirmPassword);
                }
            });
        }
    }

    /**
     * Add feedback container to input
     */
    function addFeedbackContainer(input) {
        if (input.nextElementSibling?.classList.contains('validation-feedback')) {
            return; // Already exists
        }

        const feedback = document.createElement('div');
        feedback.className = 'validation-feedback';
        input.parentElement.style.position = 'relative';
        input.after(feedback);
    }

    /**
     * Validate single input
     */
    function validateInput(input) {
        const value = input.value.trim();
        const type = input.type;
        const name = input.name.toLowerCase();
        const required = input.hasAttribute('required') || input.dataset.required;

        // Remove previous validation state
        input.classList.remove('is-valid', 'is-invalid');
        clearFeedback(input);

        // Check if empty and required
        if (required && !value) {
            return showInvalid(input, RULES.required.message);
        }

        // If empty and not required, mark as valid
        if (!value && !required) {
            return showValid(input);
        }

        // Email validation
        if (type === 'email' || name.includes('email')) {
            if (!RULES.email.pattern.test(value)) {
                return showInvalid(input, RULES.email.message);
            }
        }

        // Password validation
        if (type === 'password' && !name.includes('confirm')) {
            if (value.length < RULES.password.minLength) {
                return showInvalid(input, `Password must be at least ${RULES.password.minLength} characters`);
            }
            if (!RULES.password.pattern.test(value)) {
                return showInvalid(input, RULES.password.message);
            }
        }

        // Phone validation
        if (type === 'tel' || name.includes('phone')) {
            if (!RULES.phone.pattern.test(value) || value.replace(/\D/g, '').length < RULES.phone.minLength) {
                return showInvalid(input, RULES.phone.message);
            }
        }

        // Username validation
        if (name.includes('username')) {
            if (!RULES.username.pattern.test(value)) {
                return showInvalid(input, RULES.username.message);
            }
        }

        // Zipcode validation
        if (name.includes('zip') || name.includes('postal')) {
            if (!RULES.zipcode.pattern.test(value)) {
                return showInvalid(input, RULES.zipcode.message);
            }
        }

        // Custom pattern validation
        if (input.pattern) {
            const regex = new RegExp(input.pattern);
            if (!regex.test(value)) {
                return showInvalid(input, input.dataset.patternMessage || 'Invalid format');
            }
        }

        // Min length validation
        if (input.minLength && value.length < input.minLength) {
            return showInvalid(input, `Minimum length is ${input.minLength} characters`);
        }

        // Max length validation
        if (input.maxLength && input.maxLength > 0 && value.length > input.maxLength) {
            return showInvalid(input, `Maximum length is ${input.maxLength} characters`);
        }

        // Number validation
        if (type === 'number') {
            const num = parseFloat(value);
            if (isNaN(num)) {
                return showInvalid(input, 'Please enter a valid number');
            }
            if (input.min !== '' && num < parseFloat(input.min)) {
                return showInvalid(input, `Minimum value is ${input.min}`);
            }
            if (input.max !== '' && num > parseFloat(input.max)) {
                return showInvalid(input, `Maximum value is ${input.max}`);
            }
        }

        // All validations passed
        return showValid(input);
    }

    /**
     * Validate password confirmation match
     */
    function validatePasswordMatch(password, confirmPassword) {
        if (password.value !== confirmPassword.value) {
            return showInvalid(confirmPassword, 'Passwords do not match');
        } else {
            return showValid(confirmPassword);
        }
    }

    /**
     * Show invalid state
     */
    function showInvalid(input, message) {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
        
        const feedback = input.nextElementSibling;
        if (feedback && feedback.classList.contains('validation-feedback')) {
            feedback.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
            feedback.className = 'validation-feedback invalid-feedback';
            feedback.style.display = 'block';
        }

        return false;
    }

    /**
     * Show valid state
     */
    function showValid(input) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        
        const feedback = input.nextElementSibling;
        if (feedback && feedback.classList.contains('validation-feedback')) {
            feedback.innerHTML = '<i class="fas fa-check-circle"></i> Looks good!';
            feedback.className = 'validation-feedback valid-feedback';
            feedback.style.display = 'block';
        }

        return true;
    }

    /**
     * Clear feedback
     */
    function clearFeedback(input) {
        const feedback = input.nextElementSibling;
        if (feedback && (feedback.classList.contains('validation-feedback') || 
                         feedback.classList.contains('invalid-feedback') || 
                         feedback.classList.contains('valid-feedback'))) {
            feedback.style.display = 'none';
            feedback.innerHTML = '';
        }
    }

    /**
     * Show form-level error
     */
    function showFormError(form, message) {
        // Remove existing error
        const existingError = form.querySelector('.form-error-message');
        if (existingError) existingError.remove();

        // Create error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error-message alert alert-danger';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        
        // Insert at top of form
        form.insertBefore(errorDiv, form.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            errorDiv.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => errorDiv.remove(), 300);
        }, 5000);
    }

    /**
     * Public API
     */
    window.FormValidation = {
        validate: validateInput,
        validateForm: function(formSelector) {
            const form = document.querySelector(formSelector);
            if (form) setupFormValidation(form);
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

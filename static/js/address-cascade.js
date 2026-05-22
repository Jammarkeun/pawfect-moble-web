/**
 * Philippine Address Cascading Module
 * Automatically populates Province, City, Barangay, and Street dropdowns
 * Based on user selection with data from Philippine PSGC API
 */

class PhilippineAddressCascade {
    constructor(config) {
        this.config = {
            countrySelect: null,
            provinceSelect: null,
            citySelect: null,
            barangaySelect: null,
            streetInput: null,
            houseNumberInput: null,
            onAddressChange: null,
            autoFillAddress: false,
            addressTextarea: null,
            apiBasePath: '/api/ph',
            ...config
        };

        this.apiBasePath = this.config.apiBasePath || '/api/ph';
        this.maxRetries = 3;
        this.retryDelayMs = 1500;

        this.data = {
            regions: [],
            provinces: [],
            cities: [],
            barangays: []
        };

        this.init();
    }

    getLocationFromCollection(collection, identifier) {
        if (!Array.isArray(collection) || !identifier) return null;
        const normalized = String(identifier).toLowerCase();
        return collection.find(item => {
            if (!item) return false;
            return (
                item.code === identifier ||
                item.name === identifier ||
                (item.code && String(item.code).toLowerCase() === normalized) ||
                (item.name && item.name.toLowerCase() === normalized)
            );
        }) || null;
    }

    getSelectedOptionMeta(selectEl) {
        if (!selectEl || selectEl.selectedIndex < 0) return null;
        const option = selectEl.options[selectEl.selectedIndex];
        return {
            code: option?.dataset?.code || option?.value || '',
            name: option?.dataset?.name || option?.textContent || option?.value || ''
        };
    }

    init() {
        if (this.config.countrySelect) {
            this.setupCountrySelect();
        }
        if (this.config.provinceSelect) {
            this.loadProvinces();
        }
        this.setupEventListeners();
    }

    setupCountrySelect() {
        const countrySelect = this.config.countrySelect;
        if (!countrySelect) return;

        // Set default to Philippines
        if (!countrySelect.value) {
            countrySelect.value = 'Philippines';
        }

        countrySelect.addEventListener('change', () => {
            if (countrySelect.value === 'Philippines') {
                this.showPhilippineFields();
                this.loadProvinces();
            } else {
                this.hidePhilippineFields();
            }
        });
    }

    showPhilippineFields() {
        const fields = [
            this.config.provinceSelect,
            this.config.citySelect,
            this.config.barangaySelect
        ];

        fields.forEach(field => {
            if (field && field.closest('.form-group, .mb-3')) {
                field.closest('.form-group, .mb-3').style.display = '';
            }
        });
    }

    hidePhilippineFields() {
        const fields = [
            this.config.provinceSelect,
            this.config.citySelect,
            this.config.barangaySelect
        ];

        fields.forEach(field => {
            if (field && field.closest('.form-group, .mb-3')) {
                field.closest('.form-group, .mb-3').style.display = 'none';
            }
        });
    }

    setupEventListeners() {
        if (this.config.provinceSelect) {
            this.config.provinceSelect.addEventListener('change', (e) => {
                const optionMeta = this.getSelectedOptionMeta(e.target);
                const provinceIdentifier = optionMeta?.code || e.target.value;
                this.loadCities(provinceIdentifier);
                this.updateFullAddress();
            });
        }

        if (this.config.citySelect) {
            this.config.citySelect.addEventListener('change', (e) => {
                const optionMeta = this.getSelectedOptionMeta(e.target);
                const cityIdentifier = optionMeta?.code || e.target.value;
                this.loadBarangays(cityIdentifier);
                this.updateFullAddress();
            });
        }

        if (this.config.barangaySelect) {
            this.config.barangaySelect.addEventListener('change', () => {
                this.updateFullAddress();
            });
        }

        if (this.config.streetInput) {
            this.config.streetInput.addEventListener('change', () => {
                this.updateFullAddress();
            });
        }

        if (this.config.houseNumberInput) {
            this.config.houseNumberInput.addEventListener('change', () => {
                this.updateFullAddress();
            });
        }
    }

    async loadProvinces() {
        const provinceSelect = this.config.provinceSelect;
        if (!provinceSelect) return;

        try {
            provinceSelect.innerHTML = '<option value="">Loading provinces...</option>';
            this.showReloadButton(provinceSelect, 'province');

            // Using local API endpoint with retry logic
            const data = await this.fetchWithRetry(`${this.apiBasePath}/provinces`);

            if (data.success) {
                this.data.provinces = data.data;

                provinceSelect.innerHTML = '<option value="">Select Province</option>';
                data.data.forEach(province => {
                    const option = document.createElement('option');
                    option.value = province.name;
                    option.textContent = province.name;
                    option.dataset.code = province.code || province.name;
                    option.dataset.name = province.name;
                    provinceSelect.appendChild(option);
                });

                // Preserve existing value if any
                const initialCode = provinceSelect.dataset.initialCode;
                const currentValue = provinceSelect.dataset.initialValue;
                const match = Array.from(provinceSelect.options).find(option => {
                    if (!option.value) return false;
                    if (initialCode && option.dataset.code === initialCode) return true;
                    return currentValue && option.value === currentValue;
                });
                if (match) {
                    match.selected = true;
                    const identifier = match.dataset.code || match.value;
                    this.loadCities(identifier);
                }
                delete provinceSelect.dataset.initialValue;
                delete provinceSelect.dataset.initialCode;
                
                this.hideReloadButton(provinceSelect);
            } else {
                throw new Error('API returned error');
            }
        } catch (error) {
            console.error('Error loading provinces:', error);
            this.showErrorWithRetry(provinceSelect, 'province', error);
            this.loadProvincesFallback();
        }
    }

    async fetchWithRetry(url, attempt = 1) {
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                timeout: 8000
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            if (attempt < this.maxRetries) {
                console.warn(`Attempt ${attempt} failed. Retrying in ${this.retryDelayMs}ms...`, error);
                await new Promise(resolve => setTimeout(resolve, this.retryDelayMs));
                return this.fetchWithRetry(url, attempt + 1);
            } else {
                throw new Error(`Failed after ${this.maxRetries} attempts: ${error.message}`);
            }
        }
    }

    showReloadButton(parentSelect, type) {
        // Remove existing reload button if present
        const existingBtn = parentSelect.parentElement?.querySelector('.address-reload-btn');
        if (existingBtn) existingBtn.remove();
    }

    hideReloadButton(parentSelect) {
        const btn = parentSelect.parentElement?.querySelector('.address-reload-btn');
        if (btn) btn.remove();
    }

    showErrorWithRetry(selectElement, type, error) {
        const parent = selectElement.parentElement;
        if (!parent) return;

        // Remove existing error message and button
        const existingError = parent.querySelector('.address-error-msg');
        const existingBtn = parent.querySelector('.address-reload-btn');
        if (existingError) existingError.remove();
        if (existingBtn) existingBtn.remove();

        // Create error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'address-error-msg alert alert-warning mt-2';
        errorDiv.style.cssText = 'font-size: 0.85rem; padding: 8px 12px; border-radius: 6px;';
        errorDiv.innerHTML = `
            <strong>⚠️ Unable to load ${type === 'province' ? 'provinces' : type === 'city' ? 'cities' : 'barangays'}.</strong> 
            Please check your connection and try again. Using fallback options.
        `;
        parent.appendChild(errorDiv);

        // Create reload button
        const reloadBtn = document.createElement('button');
        reloadBtn.className = 'address-reload-btn btn btn-sm btn-outline-secondary mt-2';
        reloadBtn.type = 'button';
        reloadBtn.innerHTML = '<i class="fas fa-redo"></i> Reload';
        reloadBtn.style.cssText = 'padding: 6px 12px; font-size: 0.85rem;';

        reloadBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (type === 'province') {
                this.loadProvinces();
            } else if (type === 'city') {
                const provinceSelect = this.config.provinceSelect;
                if (provinceSelect && provinceSelect.value) {
                    const optionMeta = this.getSelectedOptionMeta(provinceSelect);
                    this.loadCities(optionMeta?.code || provinceSelect.value);
                }
            } else if (type === 'barangay') {
                const citySelect = this.config.citySelect;
                if (citySelect && citySelect.value) {
                    const optionMeta = this.getSelectedOptionMeta(citySelect);
                    this.loadBarangays(optionMeta?.code || citySelect.value);
                }
            }
        });

        parent.appendChild(reloadBtn);
    }

    loadProvincesFallback() {
        // Fallback with major provinces if API fails
        const provinceSelect = this.config.provinceSelect;
        if (!provinceSelect) return;

        const majorProvinces = [
            'Metro Manila', 'Cebu', 'Davao del Sur', 'Cavite', 'Laguna',
            'Rizal', 'Bulacan', 'Pampanga', 'Batangas', 'Pangasinan',
            'Benguet', 'Iloilo', 'Negros Occidental', 'Leyte', 'Misamis Oriental'
        ].sort();

        provinceSelect.innerHTML = '<option value="">Select Province</option>';
        majorProvinces.forEach(province => {
            const option = document.createElement('option');
            option.value = province;
            option.textContent = province;
            option.dataset.name = province;
            option.dataset.code = province;
            provinceSelect.appendChild(option);
        });
    }

    async loadCities(provinceIdentifier) {
        const citySelect = this.config.citySelect;
        if (!citySelect || !provinceIdentifier) {
            if (citySelect) {
                citySelect.innerHTML = '<option value="">Select City/Municipality</option>';
                citySelect.disabled = true;
            }
            if (this.config.barangaySelect) {
                this.config.barangaySelect.innerHTML = '<option value="">Select Barangay</option>';
                this.config.barangaySelect.disabled = true;
            }
            return;
        }

        const provinceMeta = this.getLocationFromCollection(this.data.provinces, provinceIdentifier);
        const provinceCode = provinceMeta ? provinceMeta.code : provinceIdentifier;

        try {
            citySelect.innerHTML = '<option value="">Loading cities...</option>';
            this.showReloadButton(citySelect, 'city');

            // Using local API endpoint with retry logic
            const data = await this.fetchWithRetry(`${this.apiBasePath}/cities/` + encodeURIComponent(provinceCode));

            if (data.success) {
                this.data.cities = data.data;

                citySelect.innerHTML = '<option value="">Select City/Municipality</option>';
                data.data.forEach(city => {
                    const option = document.createElement('option');
                    option.value = city.name;
                    option.textContent = city.name;
                    option.dataset.code = city.code || city.name;
                    option.dataset.name = city.name;
                    citySelect.appendChild(option);
                });

                // Clear barangay select
                if (this.config.barangaySelect) {
                    this.config.barangaySelect.innerHTML = '<option value="">Select Barangay</option>';
                }

                // Preserve existing value if any
                const initialCode = citySelect.dataset.initialCode;
                const currentValue = citySelect.dataset.initialValue;
                const match = Array.from(citySelect.options).find(option => {
                    if (!option.value) return false;
                    if (initialCode && option.dataset.code === initialCode) return true;
                    return currentValue && option.value === currentValue;
                });
                if (match) {
                    match.selected = true;
                    const identifier = match.dataset.code || match.value;
                    this.loadBarangays(identifier);
                }
                delete citySelect.dataset.initialValue;
                delete citySelect.dataset.initialCode;
                
                this.hideReloadButton(citySelect);
            } else {
                throw new Error('API returned error');
            }
        } catch (error) {
            console.error('Error loading cities:', error);
            this.showErrorWithRetry(citySelect, 'city', error);
            citySelect.innerHTML = '<option value="">Select City/Municipality</option>';
        }
    }

    async loadBarangays(cityIdentifier) {
        const barangaySelect = this.config.barangaySelect;
        if (!barangaySelect || !cityIdentifier) {
            if (barangaySelect) {
                barangaySelect.innerHTML = '<option value="">Select Barangay</option>';
                barangaySelect.disabled = true;
            }
            return;
        }

        const cityMeta = this.getLocationFromCollection(this.data.cities, cityIdentifier);
        const cityCode = cityMeta ? cityMeta.code : cityIdentifier;

        try {
            barangaySelect.innerHTML = '<option value="">Loading barangays...</option>';
            this.showReloadButton(barangaySelect, 'barangay');

            // Using local API endpoint with retry logic
            const data = await this.fetchWithRetry(`${this.apiBasePath}/barangays/${encodeURIComponent(cityCode)}`);

            if (data.success) {
                this.data.barangays = data.data;

                barangaySelect.innerHTML = '<option value="">Select Barangay</option>';
                data.data.forEach(barangay => {
                    const option = document.createElement('option');
                    option.value = barangay.name;
                    option.textContent = barangay.name;
                    option.dataset.code = barangay.code || barangay.name;
                    option.dataset.name = barangay.name;
                    barangaySelect.appendChild(option);
                });

                // Preserve existing value if any
                const initialCode = barangaySelect.dataset.initialCode;
                const currentValue = barangaySelect.dataset.initialValue;
                const match = Array.from(barangaySelect.options).find(option => {
                    if (!option.value) return false;
                    if (initialCode && option.dataset.code === initialCode) return true;
                    return currentValue && option.value === currentValue;
                });
                if (match) {
                    match.selected = true;
                }
                delete barangaySelect.dataset.initialValue;
                delete barangaySelect.dataset.initialCode;
                
                this.hideReloadButton(barangaySelect);
            } else {
                throw new Error('API returned error');
            }
        } catch (error) {
            console.error('Error loading barangays:', error);
            this.showErrorWithRetry(barangaySelect, 'barangay', error);
            barangaySelect.innerHTML = '<option value="">Select Barangay</option>';
        }
    }

    updateFullAddress() {
        if (!this.config.autoFillAddress || !this.config.addressTextarea) return;

        const parts = [];

        if (this.config.houseNumberInput && this.config.houseNumberInput.value) {
            parts.push(this.config.houseNumberInput.value);
        }

        if (this.config.streetInput && this.config.streetInput.value) {
            parts.push(this.config.streetInput.value);
        }

        if (this.config.barangaySelect && this.config.barangaySelect.value) {
            const barangayMeta = this.getSelectedOptionMeta(this.config.barangaySelect);
            parts.push('Barangay ' + (barangayMeta?.name || this.config.barangaySelect.value));
        }

        if (this.config.citySelect) {
            const cityMeta = this.getSelectedOptionMeta(this.config.citySelect);
            if (cityMeta?.name) {
                parts.push(cityMeta.name);
            }
        }

        if (this.config.provinceSelect) {
            const provinceMeta = this.getSelectedOptionMeta(this.config.provinceSelect);
            if (provinceMeta?.name) {
                parts.push(provinceMeta.name);
            }
        }

        if (this.config.countrySelect && this.config.countrySelect.value) {
            parts.push(this.config.countrySelect.value);
        }

        const fullAddress = parts.join(', ');
        this.config.addressTextarea.value = fullAddress;

        if (this.config.onAddressChange) {
            this.config.onAddressChange(fullAddress);
        }
    }

    // Set initial values (useful when editing existing data)
    setInitialValues(values) {
        if (values.province && this.config.provinceSelect) {
            this.config.provinceSelect.dataset.initialValue = values.province;
        }
        if (values.provinceCode && this.config.provinceSelect) {
            this.config.provinceSelect.dataset.initialCode = values.provinceCode;
        }
        if (values.city && this.config.citySelect) {
            this.config.citySelect.dataset.initialValue = values.city;
        }
        if (values.cityCode && this.config.citySelect) {
            this.config.citySelect.dataset.initialCode = values.cityCode;
        }
        if (values.barangay && this.config.barangaySelect) {
            this.config.barangaySelect.dataset.initialValue = values.barangay;
        }
        if (values.barangayCode && this.config.barangaySelect) {
            this.config.barangaySelect.dataset.initialCode = values.barangayCode;
        }
        if (values.street && this.config.streetInput) {
            this.config.streetInput.value = values.street;
        }
        if (values.houseNumber && this.config.houseNumberInput) {
            this.config.houseNumberInput.value = values.houseNumber;
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PhilippineAddressCascade;
}

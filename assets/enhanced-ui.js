/**
 * Enhanced UI JavaScript for MELD Visualizer
 * Handles client-side interactions for enhanced desktop UI components
 */

class EnhancedUIManager {
    constructor() {
        this.toasts = new Map();
        this.scrollPositions = new Map();
        this.init();
    }

    init() {
        this.initTabScrolling();
        this.initToastSystem();
        this.initProgressSystem();
        this.initCollapsiblePanels();
        this.initUploadEnhancements();
        this.initKeyboardNavigation();
    }

    /**
     * Initialize tab scrolling functionality
     */
    initTabScrolling() {
        const leftButton = document.getElementById('tab-scroll-left');
        const rightButton = document.getElementById('tab-scroll-right');
        const scrollContainer = document.querySelector('.enhanced-tabs-scroll-container');

        if (!leftButton || !rightButton || !scrollContainer) return;

        // Scroll amount based on viewport width
        const getScrollAmount = () => {
            return Math.min(200, scrollContainer.clientWidth * 0.3);
        };

        leftButton.addEventListener('click', () => {
            const scrollAmount = getScrollAmount();
            scrollContainer.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        });

        rightButton.addEventListener('click', () => {
            const scrollAmount = getScrollAmount();
            scrollContainer.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        });

        // Update button states based on scroll position
        const updateScrollButtons = () => {
            const isAtStart = scrollContainer.scrollLeft <= 0;
            const isAtEnd = scrollContainer.scrollLeft >= 
                scrollContainer.scrollWidth - scrollContainer.clientWidth - 1;

            leftButton.disabled = isAtStart;
            rightButton.disabled = isAtEnd;

            leftButton.style.opacity = isAtStart ? '0.3' : '1';
            rightButton.style.opacity = isAtEnd ? '0.3' : '1';
        };

        scrollContainer.addEventListener('scroll', updateScrollButtons);
        
        // Initial update
        setTimeout(updateScrollButtons, 100);
        
        // Update on resize
        window.addEventListener('resize', () => {
            setTimeout(updateScrollButtons, 100);
        });
    }

    /**
     * Initialize toast notification system
     */
    initToastSystem() {
        this.createToastContainer();
        this.setupToastEventListeners();
    }

    createToastContainer() {
        if (document.getElementById('toast-container')) return;

        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    /**
     * Show a toast notification
     * @param {Object} config - Toast configuration
     */
    showToast(config) {
        const {
            id = `toast-${Date.now()}`,
            type = 'info',
            title = 'Notification',
            message = '',
            duration = 5000,
            icon = 'fas fa-info-circle'
        } = config;

        const toast = this.createToastElement(id, type, title, message, icon, duration);
        const container = document.getElementById('toast-container');
        
        if (!container) return;

        container.appendChild(toast);
        this.toasts.set(id, { element: toast, duration });

        // Show animation
        setTimeout(() => toast.classList.add('show'), 10);

        // Auto-dismiss
        if (duration > 0) {
            setTimeout(() => this.removeToast(id), duration);
        }

        // Store toast for potential removal
        return id;
    }

    createToastElement(id, type, title, message, icon, duration) {
        const toast = document.createElement('div');
        toast.className = `enhanced-toast ${type}`;
        toast.id = id;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');

        toast.innerHTML = `
            <div class="toast-header">
                <i class="${icon} toast-icon"></i>
                <h6 class="toast-title">${title}</h6>
                <button type="button" class="toast-close" aria-label="Close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="toast-body">${message}</div>
            ${duration > 0 ? `<div class="toast-progress"><div class="toast-progress-bar"></div></div>` : ''}
        `;

        // Add close button functionality
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.removeToast(id));

        return toast;
    }

    /**
     * Remove a toast notification
     * @param {string} toastId - Toast ID to remove
     */
    removeToast(toastId) {
        const toastData = this.toasts.get(toastId);
        if (!toastData) return;

        const toast = toastData.element;
        toast.classList.remove('show');
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            this.toasts.delete(toastId);
        }, 300);
    }

    setupToastEventListeners() {
        // Listen for Dash callbacks to trigger toasts
        if (window.dash_clientside) {
            window.addEventListener('dash-toast', (event) => {
                this.showToast(event.detail);
            });
        }
    }

    /**
     * Initialize progress indicator system
     */
    initProgressSystem() {
        this.setupProgressUpdates();
    }

    /**
     * Update progress indicator
     * @param {string} progressId - Progress indicator ID
     * @param {number} value - Progress value
     * @param {number} maxValue - Maximum value
     */
    updateProgress(progressId, value, maxValue = 100) {
        const progressBar = document.getElementById(`${progressId}-bar`);
        const progressText = progressBar?.querySelector('.progress-text');

        if (!progressBar || !progressText) return;

        const percentage = Math.min(100, Math.max(0, (value / maxValue) * 100));
        
        progressBar.style.width = `${percentage}%`;
        progressText.textContent = `${Math.round(percentage)}%`;

        // Add completion styling
        if (percentage >= 100) {
            progressBar.classList.add('completed');
            setTimeout(() => {
                this.showToast({
                    type: 'success',
                    title: 'Task Complete',
                    message: 'Operation completed successfully!',
                    duration: 3000
                });
            }, 500);
        }
    }

    setupProgressUpdates() {
        // Listen for progress updates from Dash callbacks
        if (window.dash_clientside) {
            window.addEventListener('dash-progress', (event) => {
                const { progressId, value, maxValue } = event.detail;
                this.updateProgress(progressId, value, maxValue);
            });
        }
    }

    /**
     * Initialize collapsible panel functionality
     */
    initCollapsiblePanels() {
        document.addEventListener('click', (event) => {
            const header = event.target.closest('.control-panel-header');
            if (!header) return;

            const icon = header.querySelector('.collapse-icon');
            if (!icon) return;

            header.classList.toggle('collapsed');
            
            // Let Bootstrap handle the collapse, just update the icon
            const targetId = header.getAttribute('data-bs-target');
            if (targetId) {
                const target = document.querySelector(targetId);
                if (target) {
                    // Listen for Bootstrap collapse events
                    target.addEventListener('shown.bs.collapse', () => {
                        header.classList.remove('collapsed');
                    });
                    target.addEventListener('hidden.bs.collapse', () => {
                        header.classList.add('collapsed');
                    });
                }
            }
        });
    }

    /**
     * Initialize enhanced upload functionality
     */
    initUploadEnhancements() {
        document.addEventListener('dragover', (event) => {
            const uploadArea = event.target.closest('.enhanced-upload-area');
            if (uploadArea) {
                event.preventDefault();
                uploadArea.classList.add('dragover');
            }
        });

        document.addEventListener('dragleave', (event) => {
            const uploadArea = event.target.closest('.enhanced-upload-area');
            if (uploadArea && !uploadArea.contains(event.relatedTarget)) {
                uploadArea.classList.remove('dragover');
            }
        });

        document.addEventListener('drop', (event) => {
            const uploadArea = event.target.closest('.enhanced-upload-area');
            if (uploadArea) {
                uploadArea.classList.remove('dragover');
            }
        });
    }

    /**
     * Initialize keyboard navigation
     */
    initKeyboardNavigation() {
        document.addEventListener('keydown', (event) => {
            // Ctrl+Arrow keys for tab navigation
            if (event.ctrlKey && (event.key === 'ArrowLeft' || event.key === 'ArrowRight')) {
                this.handleTabKeyboardNavigation(event);
            }
            
            // Escape to close modals/toasts
            if (event.key === 'Escape') {
                this.handleEscapeKey();
            }
        });
    }

    handleTabKeyboardNavigation(event) {
        const tabs = document.querySelectorAll('.enhanced-tabs .nav-link');
        const activeTab = document.querySelector('.enhanced-tabs .nav-link.active');
        
        if (!tabs.length || !activeTab) return;

        const currentIndex = Array.from(tabs).indexOf(activeTab);
        let newIndex;

        if (event.key === 'ArrowLeft') {
            newIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
        } else {
            newIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
        }

        event.preventDefault();
        tabs[newIndex].click();
        tabs[newIndex].focus();
    }

    handleEscapeKey() {
        // Close loading overlay
        const loadingOverlay = document.querySelector('.loading-overlay.show');
        if (loadingOverlay) {
            this.hideLoading();
            return;
        }

        // Close newest toast
        const toasts = Array.from(this.toasts.values());
        if (toasts.length > 0) {
            const newestToast = toasts[toasts.length - 1];
            this.removeToast(newestToast.element.id);
        }
    }

    /**
     * Show loading overlay
     * @param {string} message - Loading message
     */
    showLoading(message = 'Processing...') {
        let overlay = document.getElementById('loading-overlay');
        
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loading-overlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-content">
                    <div class="loading-spinner"></div>
                    <p class="loading-message">${message}</p>
                </div>
            `;
            document.body.appendChild(overlay);
        } else {
            overlay.querySelector('.loading-message').textContent = message;
        }

        overlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Hide loading overlay
     */
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    /**
     * Update loading message
     * @param {string} message - New loading message
     */
    updateLoadingMessage(message) {
        const overlay = document.getElementById('loading-overlay');
        const messageElement = overlay?.querySelector('.loading-message');
        if (messageElement) {
            messageElement.textContent = message;
        }
    }

    /**
     * Utility method to trigger custom events for Dash callbacks
     * @param {string} eventName - Event name
     * @param {Object} detail - Event detail data
     */
    triggerDashEvent(eventName, detail) {
        const event = new CustomEvent(eventName, { detail });
        window.dispatchEvent(event);
    }
}

// Initialize Enhanced UI Manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedUI = new EnhancedUIManager();
});

// Expose utility functions for Dash callbacks
window.dashUtils = {
    showToast: (config) => window.enhancedUI?.showToast(config),
    showLoading: (message) => window.enhancedUI?.showLoading(message),
    hideLoading: () => window.enhancedUI?.hideLoading(),
    updateProgress: (id, value, max) => window.enhancedUI?.updateProgress(id, value, max),
    updateLoadingMessage: (message) => window.enhancedUI?.updateLoadingMessage(message)
};

// Clientside callbacks for Dash integration
if (window.dash_clientside) {
    window.dash_clientside.namespace = window.dash_clientside.namespace || {};
    
    // Toast notification callback
    window.dash_clientside.enhanced_ui = {
        show_toast: function(trigger, config) {
            if (!trigger || !config) return window.dash_clientside.no_update;
            window.dashUtils.showToast(config);
            return window.dash_clientside.no_update;
        },
        
        show_loading: function(trigger, message) {
            if (!trigger) return window.dash_clientside.no_update;
            window.dashUtils.showLoading(message || 'Processing...');
            return window.dash_clientside.no_update;
        },
        
        hide_loading: function(trigger) {
            if (!trigger) return window.dash_clientside.no_update;
            window.dashUtils.hideLoading();
            return window.dash_clientside.no_update;
        },
        
        update_progress: function(value, max_value, progress_id) {
            if (value === undefined || !progress_id) return window.dash_clientside.no_update;
            window.dashUtils.updateProgress(progress_id, value, max_value || 100);
            return window.dash_clientside.no_update;
        }
    };
}
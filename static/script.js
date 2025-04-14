// Global variables
let loadingContainer;
let body;
let themeTransitionOverlay;

// Function to initialize all event listeners
function initializeEventListeners() {
    // Input field highlighting
    const inputFields = document.querySelectorAll("input[type='text']");
    inputFields.forEach(input => {
        input.addEventListener("focus", function() {
            this.parentElement.style.boxShadow = "0 8px 25px rgba(229, 9, 20, 0.3)";
            this.parentElement.style.borderColor = "var(--primary-color)";
            this.parentElement.style.transform = "translateY(-2px)";
        });
        
        input.addEventListener("blur", function() {
            this.parentElement.style.boxShadow = "";
            this.parentElement.style.borderColor = "";
            this.parentElement.style.transform = "";
        });
    });
    
    // Movie Card Hover Effects with enhanced animations
    const movieCards = document.querySelectorAll(".movie-card");
    movieCards.forEach(card => {
        card.addEventListener("mouseenter", function() {
            this.style.transform = "translateY(-12px) scale(1.02)";
            this.style.boxShadow = body.classList.contains("dark-mode") 
                ? "0 15px 35px var(--dark-shadow)" 
                : "0 15px 35px var(--light-shadow)";
            this.style.borderColor = "var(--primary-color)";
            
            const poster = this.querySelector(".movie-poster img");
            if (poster) {
                poster.style.transform = "scale(1.08)";
            }
            
            const posterOverlay = this.querySelector(".movie-poster::after");
            if (posterOverlay) {
                posterOverlay.style.opacity = "1";
            }
            
            const title = this.querySelector(".movie-info h3");
            if (title) {
                title.style.color = "var(--primary-color)";
            }
        });
        
        card.addEventListener("mouseleave", function() {
            this.style.transform = "";
            this.style.boxShadow = "";
            this.style.borderColor = body.classList.contains("dark-mode") 
                ? "var(--dark-border)" 
                : "var(--light-border)";
            
            const poster = this.querySelector(".movie-poster img");
            if (poster) {
                poster.style.transform = "";
            }
            
            const posterOverlay = this.querySelector(".movie-poster::after");
            if (posterOverlay) {
                posterOverlay.style.opacity = "";
            }
            
            const title = this.querySelector(".movie-info h3");
            if (title) {
                title.style.color = "";
            }
        });
    });
    
    // Error message handling with improved animation
    const errorMessage = document.querySelector(".error-message");
    if (errorMessage) {
        // Animate in
        errorMessage.style.opacity = "0";
        errorMessage.style.transform = "translateY(-10px)";
        
        setTimeout(() => {
            errorMessage.style.opacity = "1";
            errorMessage.style.transform = "translateY(0)";
        }, 100);
        
        // Auto-hide error message after 5 seconds with smooth animation
        setTimeout(() => {
            errorMessage.style.opacity = "0";
            errorMessage.style.transform = "translateY(-10px)";
            setTimeout(() => {
                errorMessage.style.display = "none";
            }, 500);
        }, 5000);
    }
    
    // Initialize form submission handlers for inline forms
    const inlineForms = document.querySelectorAll("form.inline-form");
    inlineForms.forEach(form => {
        form.addEventListener("submit", handleInlineFormSubmit);
    });
    
    // Animate elements when they come into view with enhanced animations
    animateOnScroll();
    
    // Add hover effects to buttons
    const buttons = document.querySelectorAll(".btn-similar, .genre-tag");
    buttons.forEach(button => {
        button.addEventListener("mouseenter", function() {
            this.style.transform = "translateY(-3px)";
            if (this.classList.contains("btn-similar")) {
                this.style.boxShadow = "0 6px 15px rgba(229, 9, 20, 0.4)";
            } else {
                this.style.boxShadow = "0 6px 15px rgba(229, 9, 20, 0.3)";
            }
        });
        
        button.addEventListener("mouseleave", function() {
            this.style.transform = "";
            this.style.boxShadow = "";
        });
        
        button.addEventListener("mousedown", function() {
            this.style.transform = "translateY(0)";
            if (this.classList.contains("btn-similar")) {
                this.style.boxShadow = "0 2px 5px rgba(229, 9, 20, 0.3)";
            } else {
                this.style.boxShadow = "0 2px 5px rgba(229, 9, 20, 0.2)";
            }
        });
        
        button.addEventListener("mouseup", function() {
            this.style.transform = "translateY(-3px)";
            if (this.classList.contains("btn-similar")) {
                this.style.boxShadow = "0 6px 15px rgba(229, 9, 20, 0.4)";
            } else {
                this.style.boxShadow = "0 6px 15px rgba(229, 9, 20, 0.3)";
            }
        });
    });
}

// Function to handle inline form submissions with improved loading animation
function handleInlineFormSubmit(event) {
    event.preventDefault();
    
    // Show loading spinner with enhanced animation
    loadingContainer.style.display = "flex";
    setTimeout(() => {
        loadingContainer.classList.add("show");
    }, 10);
    
    const formData = new FormData(this);
    const formAction = this.getAttribute('action');
    
    fetch(formAction, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(html => {
        // Hide loading spinner with smooth transition
        loadingContainer.classList.remove("show");
        setTimeout(() => {
            loadingContainer.style.display = "none";
        }, 300);
        
        // Create a temporary div to parse the HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        
        // Extract the main content from the parsed HTML
        const newContent = tempDiv.querySelector('.container');
        const newHeroContent = tempDiv.querySelector('.hero-content');
        
        // Update only the necessary parts of the page
        if (newContent) {
            document.querySelector('.container').innerHTML = newContent.innerHTML;
        }
        
        if (newHeroContent) {
            document.querySelector('.hero-content').innerHTML = newHeroContent.innerHTML;
        }
        
        // Reinitialize event listeners for the updated content
        initializeEventListeners();
    })
    .catch(error => {
        console.error('Error:', error);
        
        // Hide loading spinner with smooth transition
        loadingContainer.classList.remove("show");
        setTimeout(() => {
            loadingContainer.style.display = "none";
        }, 300);
        
        // Show an error message with enhanced animation
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i><span>An error occurred. Please try again.</span>';
        errorDiv.style.opacity = "0";
        errorDiv.style.transform = "translateY(-10px)";
        
        const container = document.querySelector('.container');
        container.insertBefore(errorDiv, container.firstChild);
        
        // Animate in
        setTimeout(() => {
            errorDiv.style.opacity = "1";
            errorDiv.style.transform = "translateY(0)";
        }, 10);
        
        // Auto-hide error message after 5 seconds with smooth animation
        setTimeout(() => {
            errorDiv.style.opacity = "0";
            errorDiv.style.transform = "translateY(-10px)";
            setTimeout(() => {
                errorDiv.remove();
            }, 500);
        }, 5000);
    });
}

// Function to animate elements on scroll with enhanced animations
function animateOnScroll() {
    const elements = document.querySelectorAll(".movie-section, .genres-section, .browse-section");
    
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.2;
        
        if (elementPosition < screenPosition) {
            element.style.opacity = "1";
            element.style.transform = "translateY(0)";
        }
    });
}

// Function to create theme transition overlay
function createThemeTransitionOverlay() {
    // Create overlay element if it doesn't exist
    if (!document.getElementById('theme-transition-overlay')) {
        const overlay = document.createElement('div');
        overlay.id = 'theme-transition-overlay';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.3)';
        overlay.style.zIndex = '9999';
        overlay.style.opacity = '0';
        overlay.style.pointerEvents = 'none';
        overlay.style.transition = 'opacity 0.3s ease';
        document.body.appendChild(overlay);
        
        themeTransitionOverlay = overlay;
    }
}

// Function to toggle theme with smooth transition
function toggleTheme() {
    // Show overlay
    themeTransitionOverlay.style.opacity = '1';
    
    // Toggle theme after a short delay
    setTimeout(() => {
        body.classList.toggle("dark-mode");
        const currentTheme = body.classList.contains("dark-mode") ? "dark" : "light";
        localStorage.setItem("theme", currentTheme);
        
        // Hide overlay
        setTimeout(() => {
            themeTransitionOverlay.style.opacity = '0';
        }, 200);
    }, 100);
}

// Main initialization when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
    // Initialize global variables
    loadingContainer = document.getElementById("loading");
    body = document.body;
    
    // Create theme transition overlay
    createThemeTransitionOverlay();
    
    // Theme Toggle Functionality with enhanced animation
    const themeToggleBtn = document.getElementById("theme-toggle-btn");
    
    // Check for saved theme preference or use default dark theme
    const savedTheme = localStorage.getItem("theme") || "dark";
    if (savedTheme === "light") {
        body.classList.remove("dark-mode");
    } else {
        body.classList.add("dark-mode");
    }
    
    // Toggle theme when button is clicked with enhanced animation
    themeToggleBtn.addEventListener("click", toggleTheme);
    
    // Add hover effect to theme toggle button
    themeToggleBtn.addEventListener("mouseenter", function() {
        this.style.transform = "scale(1.1)";
        this.style.backgroundColor = body.classList.contains("dark-mode") 
            ? "rgba(255, 255, 255, 0.1)" 
            : "rgba(0, 0, 0, 0.05)";
    });
    
    themeToggleBtn.addEventListener("mouseleave", function() {
        this.style.transform = "";
        this.style.backgroundColor = "";
    });
    
    // Form Submission and Loading Spinner for all forms with enhanced animation
    const forms = document.querySelectorAll("form:not(.inline-form)");
    forms.forEach(form => {
        form.addEventListener("submit", function() {
            // Show loading spinner with enhanced animation
            loadingContainer.style.display = "flex";
            setTimeout(() => {
                loadingContainer.classList.add("show");
            }, 10);
            
            // Set a timeout to hide the loader after 8 seconds if server doesn't respond
            setTimeout(() => {
                if (loadingContainer.classList.contains("show")) {
                    loadingContainer.classList.remove("show");
                    setTimeout(() => {
                        loadingContainer.style.display = "none";
                    }, 300);
                }
            }, 8000);
        });
    });
    
    // Set initial state for scroll animations with enhanced properties
    const sectionsToAnimate = document.querySelectorAll(".movie-section, .genres-section, .browse-section");
    sectionsToAnimate.forEach(section => {
        section.style.opacity = "0";
        section.style.transform = "translateY(30px)";
        section.style.transition = "opacity 0.6s ease-out, transform 0.6s ease-out";
    });
    
    // Run animation on scroll
    window.addEventListener("scroll", animateOnScroll);
    
    // Add smooth scrolling for better user experience
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    
    // Initialize all event listeners
    initializeEventListeners();
});
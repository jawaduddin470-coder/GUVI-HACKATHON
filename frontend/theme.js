/**
 * theme.js - Light/Dark Mode Logic
 * Handles theme switching, persistence, and UI synchronization.
 */

(function () {
    const THEME_KEY = 'ai_detector_theme';

    // 1. Immediate Theme Application (to <html> to prevent flash)
    const savedTheme = localStorage.getItem(THEME_KEY) || 'light';
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
        // We'll add it to body as well once DOM is ready
    }

    function initThemeToggle() {
        const body = document.body;
        const html = document.documentElement;

        // Sync body class with html/saved state
        if (savedTheme === 'dark') {
            body.classList.add('dark');
        }

        const toggleBtn = document.getElementById('themeToggle');
        if (toggleBtn) {
            const icon = toggleBtn.querySelector('i');

            // Sync initial icon
            if (icon && body.classList.contains('dark')) {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            }

            toggleBtn.addEventListener('click', () => {
                const isDark = body.classList.toggle('dark');
                html.classList.toggle('dark', isDark);
                localStorage.setItem(THEME_KEY, isDark ? 'dark' : 'light');

                // Toggle icon
                if (icon) {
                    if (isDark) {
                        icon.classList.replace('fa-moon', 'fa-sun');
                    } else {
                        icon.classList.replace('fa-sun', 'fa-moon');
                    }
                }
            });
        }
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initThemeToggle);
    } else {
        initThemeToggle();
    }
})();

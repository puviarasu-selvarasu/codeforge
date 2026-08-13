// static/js/components/typingDots.js
document.addEventListener('alpine:init', () => {
    Alpine.data('typingDots', () => ({
        dots: '',
        interval: null,
        init() {
            this.interval = setInterval(() => {
                if (this.dots.length >= 3) {
                    this.dots = '';
                } else {
                    this.dots += '.';
                }
            }, 400);
        },
        destroy() {
            if (this.interval) {
                clearInterval(this.interval);
            }
        }
    }));
});
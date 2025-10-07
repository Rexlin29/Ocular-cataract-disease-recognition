document.addEventListener('DOMContentLoaded', function () {
    const canvas = document.getElementById('captchaCanvas');
    const ctx = canvas.getContext('2d');
    const captchaInput = document.getElementById('captchaInput');
    const captchaError = document.getElementById('captchaError');
    const refreshBtn = document.getElementById('refreshCaptcha');

    let captchaText = '';

    function generateCaptcha() {
        const chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
        let result = '';
        for (let i = 0; i < 6; i++) {
            result += chars[Math.floor(Math.random() * chars.length)];
        }
        captchaText = result;

        // Clear canvas and redraw captcha text
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.font = 'bold 30px "Courier New", monospace'; // Unique CAPTCHA-like font
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = '#3498db'; // Color for CAPTCHA text
        ctx.fillText(result, canvas.width / 2, canvas.height / 2);
    }

    refreshBtn.addEventListener('click', generateCaptcha);

    window.validateCaptcha = function () {
        if (captchaInput.value !== captchaText) {
            captchaError.textContent = 'Captcha does not match. Please try again.';
            return false;
        }
        return true;
    };

    // Generate first captcha
    generateCaptcha();
});

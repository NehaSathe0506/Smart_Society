// ==========================================================
// SMART SOCIETY - CLIENT-SIDE JAVASCRIPT
// ==========================================================

// ---- Mobile sidebar toggle ----
document.addEventListener("DOMContentLoaded", function () {
    const hamburger = document.getElementById("hamburgerBtn");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");

    if (hamburger && sidebar && overlay) {
        hamburger.addEventListener("click", function () {
            sidebar.classList.toggle("open");
            overlay.classList.toggle("open");
        });

        overlay.addEventListener("click", function () {
            sidebar.classList.remove("open");
            overlay.classList.remove("open");
        });
    }

    // ---- Auto-hide flash messages after 4 seconds ----
    const flashContainer = document.getElementById("flashContainer");
    if (flashContainer) {
        setTimeout(function () {
            flashContainer.style.transition = "opacity 0.5s ease";
            flashContainer.style.opacity = "0";
            setTimeout(function () {
                flashContainer.style.display = "none";
            }, 500);
        }, 4000);
    }
});

// ---- Confirmation before delete actions ----
function confirmDelete(itemName) {
    return confirm("Are you sure you want to delete this " + itemName + "? This action cannot be undone.");
}

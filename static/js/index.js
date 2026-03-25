document.addEventListener("DOMContentLoaded", function () {

/* ================= SMOOTH SCROLL ================= */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function (e) {
        const targetId = this.getAttribute("href");

        if (targetId && targetId !== "#") {
            const target = document.querySelector(targetId);

            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        }
    });
});

/* ================= HEADER SHADOW ================= */
const header = document.querySelector("header");

if (header) {
    window.addEventListener("scroll", function () {
        header.style.boxShadow =
            window.scrollY > 20
                ? "0 5px 20px rgba(0,0,0,0.15)"
                : "none";
    });
}

/* ================= ACTIVE NAV LINK ================= */
const navLinks = document.querySelectorAll("nav ul li a");

navLinks.forEach(link => {
    if (link.href === window.location.href) {
        link.classList.add("active");
    }
});

/* ================= SCROLL REVEAL ================= */
const revealElements = document.querySelectorAll(
".section, .card, .stat, .pricing-card, .about-section, .stat-card, .value-card"
);

function revealOnScroll() {
    const windowHeight = window.innerHeight;

    revealElements.forEach(el => {
        const elementTop = el.getBoundingClientRect().top;

        if (elementTop < windowHeight - 80) {
            el.style.opacity = "1";
            el.style.transform = "translateY(0)";
            el.style.transition = "all 0.6s ease";
        }
    });
}

window.addEventListener("scroll", revealOnScroll);
window.addEventListener("load", revealOnScroll);

/* ================= CARD HOVER ================= */
document.querySelectorAll(".card").forEach(card => {
    card.addEventListener("mouseenter", () => {
        card.style.transform = "translateY(-10px)";
        card.style.boxShadow = "0 15px 30px rgba(0,0,0,0.15)";
    });

    card.addEventListener("mouseleave", () => {
        card.style.transform = "translateY(0)";
        card.style.boxShadow = "none";
    });
});

/* ================= FORM SUBMISSION ================= */
const form = document.querySelector("#contactForm");

if (form) {

form.addEventListener("submit", async function(e) {

    e.preventDefault();

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    if (!data.full_name || !data.email || !data.phone) {
        alert("Please fill all required fields.");
        return;
    }

    // 🤖 CAPTCHA (if added)
    if (typeof grecaptcha !== "undefined") {
        data.captcha = grecaptcha.getResponse();
    }

    try {

        const response = await fetch("/submit-booking", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        let result;
        try {
            result = await response.json();
        } catch {
            throw new Error("Invalid server response");
        }

        console.log("Server Response:", result);

        if (response.ok && result.message === "Success") {

            alert("✅ Booking Successful! Our team will contact you.");
            form.reset();

            // Reset captcha
            if (typeof grecaptcha !== "undefined") {
                grecaptcha.reset();
            }

        } else {
            alert("❌ " + (result.message || "Booking failed"));
        }

    } catch (error) {

        console.error("Error:", error);
        alert("Network or server error. Please try again.");

    }

});

}

});
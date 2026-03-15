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

        if (window.scrollY > 20) {
            header.style.boxShadow = "0 5px 20px rgba(0,0,0,0.15)";
        } else {
            header.style.boxShadow = "none";
        }

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

/* added more elements so all sections show */

const revealElements = document.querySelectorAll(
".section, .card, .stat, .pricing-card, .about-section, .stat-card, .value-card"
);

function revealOnScroll(){

    const windowHeight = window.innerHeight;

    revealElements.forEach(el => {

        const elementTop = el.getBoundingClientRect().top;

        if(elementTop < windowHeight - 80){

            el.style.opacity = "1";
            el.style.transform = "translateY(0)";
            el.style.transition = "all 0.6s ease";

        }

    });

}

window.addEventListener("scroll", revealOnScroll);
window.addEventListener("load", revealOnScroll);

revealOnScroll();


/* ================= CARD HOVER EFFECT ================= */

const cards = document.querySelectorAll(".card");

cards.forEach(card => {

    card.addEventListener("mouseenter", function () {
        card.style.transform = "translateY(-10px)";
        card.style.boxShadow = "0 15px 30px rgba(0,0,0,0.15)";
        card.style.transition = "all 0.3s ease";
    });

    card.addEventListener("mouseleave", function () {
        card.style.transform = "translateY(0)";
        card.style.boxShadow = "none";
    });

});


/* ================= CONTACT FORM SUBMISSION ================= */

const form = document.querySelector("#contactForm");

if(form){

form.addEventListener("submit", async function(e){

    e.preventDefault();

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try{

        const response = await fetch("/submit-booking", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if(result.message === "Success"){

            alert("Booking Successful! Our team will contact you shortly.");
            form.reset();

        } else {

            alert("Booking failed. Please try again.");

        }

    }
    catch(error){

        console.error("Error:", error);
        alert("Something went wrong. Please try again.");

    }

});

}

});
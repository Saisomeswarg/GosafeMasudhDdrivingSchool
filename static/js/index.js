document.addEventListener("DOMContentLoaded", function () {

    /* Smooth scroll for anchor links */

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


    /* Header shadow on scroll */

    const header = document.querySelector("header");

    if (header) {
        window.addEventListener("scroll", () => {

            if (window.scrollY > 20) {
                header.style.boxShadow = "0 5px 20px rgba(0,0,0,0.15)";
            } else {
                header.style.boxShadow = "none";
            }

        });
    }


    /* Active navbar link */

    const navLinks = document.querySelectorAll("nav ul li a");
    const currentPage = window.location.pathname.split("/").pop();

    navLinks.forEach(link => {

        const linkPage = link.getAttribute("href");

        if (linkPage === currentPage) {
            link.classList.add("active");
        }

    });


    /* Scroll reveal animation */

    const revealElements = document.querySelectorAll(
        ".reveal, .card, .contact-form, .contact-info, .pricing-card"
    );

    function revealOnScroll() {

        const windowHeight = window.innerHeight;

        revealElements.forEach(el => {

            const elementTop = el.getBoundingClientRect().top;

            if (elementTop < windowHeight - 80) {
                el.classList.add("show");
            }

        });

    }

    window.addEventListener("scroll", revealOnScroll);
    window.addEventListener("load", revealOnScroll);


    /* Card hover animation */

    const cards = document.querySelectorAll(".card");

    cards.forEach(card => {

        card.addEventListener("mouseenter", () => {
            card.style.transform = "translateY(-10px)";
            card.style.boxShadow = "0 15px 30px rgba(0,0,0,0.15)";
            card.style.transition = "all 0.3s ease";
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "translateY(0)";
            card.style.boxShadow = "none";
        });

    });

});
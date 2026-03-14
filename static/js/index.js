document.addEventListener("DOMContentLoaded", function () {


document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function(e) {

        const targetId = this.getAttribute("href");

        if(targetId !== "#"){
            const target = document.querySelector(targetId);

            if(target){
                e.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        }

    });
});

const header = document.querySelector("header");

if(header){
    window.addEventListener("scroll", () => {

        if(window.scrollY > 20){
            header.style.boxShadow = "0 5px 20px rgba(0,0,0,0.15)";
        } else {
            header.style.boxShadow = "none";
        }

    });
}



const navLinks = document.querySelectorAll("nav ul li a");
const currentPath = window.location.pathname;

navLinks.forEach(link => {

    const linkPath = link.getAttribute("href");

    if(linkPath === currentPath){
        link.classList.add("active");
    }

});



const revealElements = document.querySelectorAll(
    ".reveal, .card, .contact-form, .contact-info, .pricing-card"
);

const revealOnScroll = () => {

    const windowHeight = window.innerHeight;

    revealElements.forEach(el => {

        const elementTop = el.getBoundingClientRect().top;

        if(elementTop < windowHeight - 80){
            el.classList.add("show");
        }

    });

};

window.addEventListener("scroll", revealOnScroll);
window.addEventListener("load", revealOnScroll);



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
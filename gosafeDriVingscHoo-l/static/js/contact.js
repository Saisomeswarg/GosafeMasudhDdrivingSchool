const form = document.getElementById("contactForm");
const modal = document.getElementById("successModal");
const closeBtn = document.querySelector(".close-btn");

form.addEventListener("submit", async function(e){

    e.preventDefault();

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try{

        const response = await fetch("http://127.0.0.1:5000/submit-booking",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify(data)

        });

        const result = await response.json();

        if(result.message === "Success"){

            modal.style.display = "flex";
            form.reset();

        }
        else{

            alert("Server error. Try again.");

        }

    }
    catch(error){

        console.log(error);
        alert("Connection error");

    }

});


closeBtn.onclick = () => modal.style.display="none";

window.onclick = (e)=>{
    if(e.target==modal){
        modal.style.display="none";
    }
}

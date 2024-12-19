

document.addEventListener("DOMContentLoaded", () => {
    
    const menuItems = document.querySelectorAll(".menu-item");
    const logout = document.getElementById("logout");
    
  

    // Handle menu navigation
    menuItems.forEach((item) => {
        item.addEventListener("click", (event) => {
            event.preventDefault();
            const path = item.getAttribute("data-path");
            console.log(`Navigating to: ${path}`); // Replace with actual navigation logic
        });
    });

    // Handle logout
    logout.addEventListener("click", () => {
        Swal.fire({
            title: "Attention!",
            html: "Déconnexion dans <b></b> millisecondes.",
            timer: 2000,
            timerProgressBar: true,
            didOpen: () => {
                const timer = Swal.getHtmlContainer().querySelector("b");
                const interval = setInterval(() => {
                    if (timer) timer.textContent = Swal.getTimerLeft();
                }, 100);
            },
        }).then((result) => {
            if (result.dismiss === Swal.DismissReason.timer) {
                console.log("Déconnecté"); // Replace with actual logout logic
                window.location.href = "/login"; // Redirect to login
            }
        });
    });
});

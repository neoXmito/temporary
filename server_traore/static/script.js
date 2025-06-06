const serverUrl = "http://localhost:5000";
window.login = function (event) {
    event.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch(`${serverUrl}/login`, {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.token && data.role) {
                // Sauvegarder le token et le rôle
                localStorage.setItem("jwt_token", data.token);
                localStorage.setItem("user_role", data.role);

                // Redirection basée sur le rôle retourné par le login
                if (data.role === 'admin') {
                    window.location.href = "/admin_dash";
                } else {
                    window.location.href = "/user_dash";
                }
            } else {
                alert("Identifiants incorrects.");
            }
        })
        .catch(error => {
            console.error("Erreur de connexion :", error);
            alert("Erreur réseau ou serveur.");
        });
};


// // Fonction pour vérifier si l'utilisateur est connecté
// function checkAuth() {
//     const token = localStorage.getItem("jwt_token");
//     const role = localStorage.getItem("user_role");

//     if (!token) {
//         // Rediriger vers la page de connexion si pas de token
//         window.location.href = "/login";
//         return false;
//     }

//     return { token, role };
// }

// // Fonction pour vérifier le rôle admin
// function requireAdmin() {
//     const auth = checkAuth();
//     if (!auth || auth.role !== 'admin') {
//         alert("Accès non autorisé");
//         window.location.href = "/user_dash";
//         return false;
//     }
//     return true;
// }

// // Fonction pour déconnecter l'utilisateur
// function logout() {
//     localStorage.removeItem("jwt_token");
//     localStorage.removeItem("user_role");
//     window.location.href = "/login";
// }

// Utilisation dans vos pages :
// Sur la page admin : requireAdmin();
// Sur toute page protégée : checkAuth();

// document.addEventListener("DOMContentLoaded", () => {
//     const auth = checkAuth(); // Vérifie que le token est là

//     if (auth) {
//         // Exemple : charger les infos depuis /dashboard
//         fetch("/dashboard", {
//             method: "GET",
//             headers: {
//                 "Authorization": `Bearer ${auth.token}`,
//                 "Content-Type": "application/json"
//             }
//         })
//             .then(res => {
//                 if (!res.ok) {
//                     throw new Error("Erreur d'accès au dashboard");
//                 }
//                 return res.json();
//             })
//             .then(data => {
//                 console.log("Dashboard info:", data);
//                 // Ici tu peux afficher des infos selon le rôle
//             })
//             .catch(error => {
//                 console.error("Erreur API dashboard:", error);
//                 logout(); // On force la déconnexion en cas d'erreur
//             });
//     }
// });


function registerUser(event) {
    event.preventDefault();  // Empêche le rechargement de la page

    const username = document.getElementById("fullname").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch(`${serverUrl}/register`, {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
    })
        .then(response => response.json())
        .then(data => {
            if (data.message === "User created successfully") {
                //alert("Inscription réussie ! Vous pouvez maintenant vous connecter.");
                window.location.href = '/login'; // redirige vers la page login
            } else {
                alert("Erreur : " + data.message);
            }
        })
        .catch(err => console.error("Erreur lors de l'inscription:", err));
}

// Load PCs on page load

function loadPCs() {
    const token = localStorage.getItem("jwt_token");
    const status = document.getElementById("status-filter").value;  // Get filter value

    fetch(`${serverUrl}/list-pcs?status=${status}`, {
        method: "GET",
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
        .then(response => response.json())
        .then(data => {
            const listDiv = document.getElementById("pc-list-content");
            listDiv.innerHTML = "";

            data.forEach(pc => {
                const pcDiv = document.createElement("div");
                pcDiv.className = "pc-item";
                pcDiv.innerHTML = `
                <strong>${pc.name} (${pc.ip})</strong> - ${pc.status}
                <button onclick="shutdownPC('${pc.ip}')">🔴 Shutdown</button>
            `;
                listDiv.appendChild(pcDiv);
            });
        })
        .catch(error => console.error("Error loading PCs:", error));
}

function shutdownPC(ip) {
    const token = localStorage.getItem("jwt_token");
    fetch(`${serverUrl}/trigger-shutdown`, {
        method: "POST",
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: ip })
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message || data.error);
            loadPCs(); // Refresh the list
        })
        .catch(error => console.error("Error shutting down PC:", error));
}

function shutdownAllOnline() {
    const token = localStorage.getItem("jwt_token");

    fetch(`${serverUrl}/shutdown-all-online`, {
        method: "POST",
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            loadPCs(); // Refresh the list
        })
        .catch(error => console.error("Error shutting down all online PCs:", error));
}

function scheduleShutdown() {
    const shutdownTime = prompt("Enter time for shutdown (24-hour format: HH:MM):");

    if (shutdownTime) {
        alert(`Shutdown scheduled for ${shutdownTime}`);
        fetch(`${serverUrl}/schedule-shutdown`, {
            method: "POST",
            headers: {
                'Authorization': `Bearer ${localStorage.getItem("jwt_token")}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ time: shutdownTime })
        })
            .then(response => response.json())
            .then(data => {
                alert(`Shutdown scheduled for ${shutdownTime}`);
            })
            .catch(error => console.error("Error scheduling shutdown:", error));
    }
}

function pingPCs() {
    const token = localStorage.getItem("jwt_token");
    fetch(`${serverUrl}/ping-pcs`, {
        method: "GET",
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
        .then(response => response.json())
        .then(data => {
            alert("Status refreshed!");
            loadPCs(); // Refresh the list
        })
        .catch(error => console.error("Error pinging PCs:", error));
}

// Auto-refresh every 30 seconds
setInterval(loadPCs, 30000);

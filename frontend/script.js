const API_URL = "/api/generate";

function goToStep2() {
    const name = document.getElementById("guest_name").value.trim();
    if (!name) {
        alert("Please enter the guest's name.");
        return;
    }
    document.getElementById("step1").classList.remove("active");
    document.getElementById("step2").classList.add("active");
}

function goToStep1() {
    document.getElementById("step2").classList.remove("active");
    document.getElementById("step1").classList.add("active");
}

function resetForm() {
    document.getElementById("guest_name").value = "";
    document.getElementById("family_members").value = "";
    document.getElementById("phone").value = "";
    
    document.getElementById("step3").classList.remove("active");
    document.getElementById("step1").classList.add("active");
}

async function sendInvitation() {
    const name = document.getElementById("guest_name").value.trim();
    const family = document.getElementById("family_members").value.trim();
    let phone = document.getElementById("phone").value.trim();
    
    if (!phone) {
        alert("Please enter a phone number.");
        return;
    }

    // Basic cleaning of phone number
    phone = phone.replace(/[^0-9]/g, '');
    if (phone.length === 10) {
        phone = "91" + phone; // Add default India country code if 10 digits
    }

    document.getElementById("step2").classList.remove("active");
    document.getElementById("loading").classList.add("active");

    try {
        const formData = new FormData();
        formData.append("guest_name", name);
        formData.append("family_members", family);

        const response = await fetch(API_URL, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Failed to generate PDF");
        }

        const blob = await response.blob();
        const fileName = `${name}_Wedding_Invitation.pdf`;
        const file = new File([blob], fileName, { type: "application/pdf" });
        
        // WhatsApp Message
        const message = "आपको सपरिवार विवाह में आमंत्रित किया जाता है।";
        
        // Helper function for fallback deep linking
        const openWhatsApp = () => {
             // trigger download first
             const url = window.URL.createObjectURL(blob);
             const a = document.createElement("a");
             a.href = url;
             a.download = fileName;
             document.body.appendChild(a);
             a.click();
             window.URL.revokeObjectURL(url);
             document.body.removeChild(a);

             // open whatsapp link
             const waLink = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
             
             // Check if we are on a mobile device to use app deep link instead ideally, but wa.me handles that well.
             document.getElementById("manualWaBtn").onclick = () => window.open(waLink, "_blank");
             window.open(waLink, "_blank");
        };

        // Attempt to use native mobile Web Share API including file
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
            try {
                await navigator.share({
                    title: "Wedding Invitation",
                    text: message,
                    files: [file]
                });
            } catch (err) {
                console.log("User cancelled or share failed", err);
                // IF share fails but it's just a cancellation, don't fallback. 
                // We show Step 3 anyway. If it was an error, user can click manual button.
                document.getElementById("manualWaBtn").onclick = () => openWhatsApp();
            }
        } else {
            // Fallback for Desktop or browsers that don't support file sharing
            openWhatsApp();
        }

        // Show Success Step
        document.getElementById("loading").classList.remove("active");
        document.getElementById("step3").classList.add("active");

    } catch (error) {
        alert("Error generating invitation: " + error.message);
        document.getElementById("loading").classList.remove("active");
        document.getElementById("step2").classList.add("active");
    }
}

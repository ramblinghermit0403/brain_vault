// Listen for messages from the web app
window.addEventListener("message", (event) => {
    // We only accept messages from ourselves
    if (event.source !== window) return;

    if (event.data.type && (event.data.type === "MEMWYRE_AUTH_SUCCESS")) {
        console.log("MemWyre Extension: Received auth token from web app");

        // Relay to background script
        chrome.runtime.sendMessage({
            action: "saveToken",
            token: event.data.token,
            refreshToken: event.data.refreshToken,
            user: event.data.user
        });
    }
});

// Basic JavaScript to handle chat messages
function sendMessage() {
    const userInput = document.getElementById("userInput").value;
    if (!userInput) return;

    // Display the user's message
    const chatBox = document.getElementById("chatBox");
    const userMessage = document.createElement("div");
    userMessage.classList.add("chat-message", "user-message");
    userMessage.textContent = userInput;
    chatBox.appendChild(userMessage);

    // Clear the input field
    document.getElementById("userInput").value = "";

    // Scroll to the bottom
    chatBox.scrollTop = chatBox.scrollHeight;

    // Simulate bot response (this could be replaced with actual API call)
    setTimeout(() => {
        const botMessage = document.createElement("div");
        botMessage.classList.add("chat-message", "bot-message");
        botMessage.textContent = "I'm here to help! (This is a simulated response)";
        chatBox.appendChild(botMessage);

        // Scroll to the bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 1000);
}

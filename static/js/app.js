document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    const startButton = document.getElementById('start');
    const stopButton = document.getElementById('stop');
    const sendButton = document.getElementById('send');
    const inputField = document.getElementById('input');
    const conversationOutput = document.getElementById('conversation-output');

    startButton.addEventListener('click', () => {
        socket.emit('message', { question: 'start', emails: [] });
    });

    stopButton.addEventListener('click', () => {
        socket.emit('message', { question: 'stop', emails: [] });
    });

    sendButton.addEventListener('click', () => {
        const message = inputField.value;
        socket.emit('message', { question: message, emails: [] });
    });

    socket.on('response', (data) => {
        const message = document.createElement('p');
        message.textContent = data.data;
        conversationOutput.appendChild(message);
    });
});
const socket = io();

document.addEventListener('DOMContentLoaded', (event) => {
    const chatMode = window.location.pathname.split('/')[2];
    socket.emit('join', chatMode);
});

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value;
    const chatMode = window.location.pathname.split('/')[2];

    socket.emit('send_message', { chat_mode: chatMode, message: message });
    messageInput.value = '';
    return false;
}

socket.on('new_message', (data) => {
    const messagesElement = document.getElementById('messages');
    const newMessageElement = document.createElement('li');
    newMessageElement.innerHTML = `<strong>${data.user}:</strong> ${data.message}`;
    messagesElement.appendChild(newMessageElement);
    messagesElement.scrollTop = messagesElement.scrollHeight; // 自动滚动到最后一条消息
});

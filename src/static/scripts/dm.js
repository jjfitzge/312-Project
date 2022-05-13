const socket = new WebSocket('ws://' + window.location.host + '/websocket');

const messageData = [];

// Called whenever data is received from the server over the WebSocket connection
socket.onmessage = function (ws_message) {
    const message = JSON.parse(ws_message.data);
    const messageType = message.messageType

    switch (messageType) {
        case 'receivedDM':
            addMessage(message);
            break;
        case 'addOnlineUser':
            addOnlineUser(message);
            break;
        case 'removeOnlineUser':
            removeOnlineUser(message);
            break;
        default:
            console.log(`received an invalid WS messageType: ${messageType}`);
    }
}
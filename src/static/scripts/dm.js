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

function getOpenDMs() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            console.log(`response: ${this.response}`);
            const openDMs = JSON.parse(this.response);
            messageData = openDMs;
            console.log(`Message Data ${messageData}`);
            // for (let user of users) {
            //     console.log(`Adding User ${user.username}`);
            //     addOnlineUser(user);
            }
        }
    request.open("GET", "/open-dms");
    request.send();
}
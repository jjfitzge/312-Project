const socket = new WebSocket('ws://' + window.location.host + '/websocket');

socket.onmessage = function (ws_message) {
    const message = JSON.parse(ws_message.data);
    const messageType = message.messageType

    switch (messageType) {
        case 'receivedNotif':
            showNotification(message);
            break;
        default:
            console.log(`received an invalid WS messageType: ${messageType}`);
    }
}

function showNotification(fromUser) {
    if (!fromUser) return;

    const notifications = document.querySelector(".notifications-container");
    const username = fromUser.username;
    const message = fromUser.comment;

    const newNotif = document.createElement('div');
    newNotif.classList.add("notification");
    newNotif.setAttribute("onclick", `goToDM("${username}");`)
    

    newNotif.innerHTML = `${username} has sent you a message!<br /><b>${username}</b>: ${message}`;
    notifications.append(newNotif);
}

function goToDM(username) {
    console.log(`went to dm ${username}`)
    if (username) {
        socket.send(JSON.stringify({ 'messageType': 'initDM', 'toUser': username }));
        const request = new XMLHttpRequest();
        request.onreadystatechange = function () {
            if (this.readyState === 4 && this.status === 200) {
                console.log("window location:", window.location);
                window.location = "dm";
            }
        };

        request.open("GET", "/redirectdm");
        request.send();
    }
}
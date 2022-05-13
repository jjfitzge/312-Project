const socket = new WebSocket('ws://' + window.location.host + '/websocket');

let messageData;
let recipient;

// Called whenever data is received from the server over the WebSocket connection
socket.onmessage = function (ws_message) {
    const message = JSON.parse(ws_message.data);
    const messageType = message.messageType

    switch (messageType) {
        case 'directMessage':
            addMessage(message);
            break;
        default:
            console.log(`received an invalid WS messageType: ${messageType}`);
    }
}

function initDMPage() {
    initRecipient();
    getOpenDMs();
}

function getOpenDMs() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            console.log(`response: ${this.response}`);
            const dms = JSON.parse(this.response);
            messageData = dms;
            console.log(`Message Data ${messageData}`);
            
            
            for (let dm of dms.openDMs) {
                addOpenDM({username: dm.otherUsersName});
            }
            // for (let user of users) {
            //     console.log(`Adding User ${user.username}`);
            //     addOnlineUser(user);
        }
    }
    request.open("GET", "/open-dms");
    request.send();
}

function initRecipient() {
    console.log("Initializing Recipient");
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(`response: ${this.response}`);
            // const data = JSON.parse(this.response);
            // setOpenMessage(data['toUser']);
            const data = this.response;
            setOpenMessage(data);

            console.log("set user to ", data);

            // const toUser = data.toUser;
            // recipient = toUser;
        }
    }
    request.open("GET", "/dm-to");
    request.send();
}

function sendDM() {
    const chatBox = document.getElementById("send-dm");
    const comment = chatBox.value;
    chatBox.value = "";
    chatBox.focus();
    if (comment !== "") {
        socket.send(JSON.stringify({ 'messageType': 'directMessage', 'toUser': recipient, 'comment': comment }));
        // socket.send(JSON.stringify({ 'messageType': 'directMessage', 'toUser': 'test', 'comment': comment }));
    }
}

function setOpenMessage(username) {
    recipient = username;
}

function changeRecipient() {

}

function addOpenDM(user) {
    const openDMList = document.getElementsByClassName('open-dms')[0];

    const newDiv = document.createElement('div');
    newDiv.classList.add("openDM-list-item");
    const username = user['username'];
    newDiv.setAttribute("onclick", "setOpenMessage(this.innerText);")
    newDiv.innerHTML = `<b>${username}</b>`;

    openDMList.append(newDiv);

}
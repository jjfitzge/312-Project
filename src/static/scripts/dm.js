const socket = new WebSocket('ws://' + window.location.host + '/websocket');

let messageData;
let recipient;

// Called whenever data is received from the server over the WebSocket connection
socket.onmessage = function (ws_message) {
    const message = JSON.parse(ws_message.data);
    const messageType = message.messageType
    console.dir(`Received websocket message of type: ${messageType}\n${message}\n\n${JSON.stringify(message)}`)

    switch (messageType) {
        case 'directMessage':
            addWebsocketMessage(message);
            break;
        case 'receivedNotif':
            showNotification(message);
            break;
        default:
            console.log(`received an invalid WS messageType: ${messageType}`);
    }
}

function initDMPage() {
    initRecipient();
    getOpenDMs();
    // if(messageData)
    //     showMessages(messageData);
    // else console.log("No message data yet...");
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
            showMessages(messageData, recipient);
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
            const data = this.response;
            console.log(`Datatype: ${(typeof data)}`)
            const toUser = data.slice(1, data.length-1); // Remove quotations from the data
            recipient = toUser;

            console.log("set user to ", toUser);
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

function setRecipient(username) {
    console.log(`Set recipient to ${username}`);
    recipient = username;
    refreshMessagePane(username);
}

function refreshMessagePane(newRecipient) {
    // deleteMessages();
    // showMessages(messageData, newRecipient)
}

function deleteMessages() {
    // const messageList = 
    const messageView = document.getElementsByClassName('messages-list')[0];
    messageView.remove();
}

function addOpenDM(user) {
    const openDMList = document.getElementsByClassName('open-dms')[0];

    const newDiv = document.createElement('div');
    newDiv.classList.add("openDM-list-item");
    const username = user['username'];
    newDiv.setAttribute("onclick", "setRecipient(this.innerText);")
    newDiv.innerHTML = `<b>${username}</b>`;

    openDMList.append(newDiv);

}

function addWebsocketMessage(data) {
    const username = data['username'];
    const toUser = data['toUser'];
    console.log(`Sent from ${username} to ${toUser}`)
    console.log(`current recipient: ${recipient}`);
    // if (username !== recipient && username !== toUser) return;

    const message = data['comment'];
    const color = data['color'];

    const messageView = document.getElementsByClassName('chat-view')[0];
    const newMsgDiv = document.createElement('div');
    newMsgDiv.innerHTML += `<div class="message-container"><b>${username}:</b> ${message}</div>`;

    messageView.prepend(newMsgDiv);
}

function showMessages(data, otherUser) {
    if (!data || !otherUser) return;

    const messageView = document.getElementsByClassName('chat-view')[0];

    const currentUser = data['currentUser'];
    const openDMs = data['openDMs'];
    const messages = getParticularMessages(openDMs, otherUser);

    console.log(`=== Data ===\ncurrentUser: ${currentUser}\nopenDMs:${openDMs}`);

    const allMsgDiv = document.createElement('div');
    allMsgDiv.classList.add('messages-list');
    for (let msg of messages)
        allMsgDiv.innerHTML += `<div class="message-container"><b>${msg.username}:</b> ${msg.comment}</div>`;

    messageView.append(allMsgDiv);

    console.log('printingDMs');
    for (let msg of messages) {
        console.log(msg);
        console.log(msg.username, msg.comment)
    }
}

function getParticularMessages(openDMs, otherUser) {
    let messages;
    console.log(`Iterating open dms ${openDMs}`)
    for (let dm of openDMs) {
        if (dm.otherUsersName === otherUser) {
            messages = dm.messages;
        }
    }
    console.log(`Returning messages: ${JSON.stringify(messages)}`);
    return messages;
}

function createMessage(msg) {
    const newMsg = document.createElement('div');
    newdiv.classList.add('message-container');
    // const username = 

}

function showNotification(fromUser) {
    if (!fromUser) return;

    const notifications = document.querySelector(".notifications-container");
    const username = fromUser.username;

    const newNotif = document.createElement('div');
    newNotif.classList.add("notification");
    newNotif.setAttribute("onclick", `goToDM("${username}");`)
    

    newNotif.innerHTML = `${username} has sent you a message!`;
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
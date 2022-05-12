console.log("Starting Script");
// getOnlineUsers();
const socket = new WebSocket('ws://' + window.location.host + '/websocket');

function sendMessage() {
    const chatBox = document.getElementById("send-input");
    const comment = chatBox.value;
    chatBox.value = "";
    chatBox.focus();
    if (comment !== "") {
        socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': comment}));
    }
}

document.addEventListener("keypress", function (event) {
    if (event.code === "Enter") {
        sendMessage();
    }
});

// let chatBackground = 0;

// Renders a new chat message to the page
function addMessage(chatMessage) {
    let chatview = document.getElementsByClassName('chat-view')[0];
    const newDiv = document.createElement('div');
    newDiv.classList.add("chat-message");

    newDiv.innerHTML = ("<b>" + chatMessage['username'] + "</b>: " + chatMessage["comment"] + "<br/>");
    chatview.prepend(newDiv);

    // chatview.innerHTML += "<b>" + chatMessage['username'] + "</b>: " + chatMessage["comment"] + "<br/>";
}

// called when the page loads to get the chat_history
function get_chat_history() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessage(message);
            }
        }
    };
    request.open("GET", "/chat-history");
    request.send();
}

// Called whenever data is received from the server over the WebSocket connection
socket.onmessage = function (ws_message) {
    const message = JSON.parse(ws_message.data);
    const messageType = message.messageType

    switch (messageType) {
        case 'chatMessage':
            addMessage(message);
            break;
        case 'addOnlineUser':
            addOnlineUser(message);
            break;
        case 'removeOnlineUser':
            removeOnlineUser(message);
            break;
        case 'webRTC-offer':
            webRTCConnection.setRemoteDescription(new RTCSessionDescription(message.offer));
            webRTCConnection.createAnswer().then(answer => {
                webRTCConnection.setLocalDescription(answer);
                socket.send(JSON.stringify({'messageType': 'webRTC-answer', 'answer': answer}));
            });
            break;
        case 'webRTC-answer':
            webRTCConnection.setRemoteDescription(new RTCSessionDescription(message.answer));
            break;
        case 'webRTC-candidate':
            webRTCConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
            break;
        default:
            console.log(`received an invalid WS messageType: ${messageType}`);
    }
}



/*
	addOnlineUser
  	    Parameters:	    user - a user's information in JSON format
	    Return Value:	none
	Description:
        Creates a new div and adds a user to the userlist using the the data in the passed in user object
*/
function addOnlineUser(user) {
    const userList = document.getElementsByClassName('user-list-view')[0];
    const onlineUsers = userList.querySelectorAll('.user-list-item');

    for (u of onlineUsers) {
        console.log("inner text", u.innerText);
        if (u.innerText === user['username']) {
            console.log(`Duplicate: ${u.username}`);
            return;
        }
    }

    const newDiv = document.createElement('div');
    newDiv.classList.add("user-list-item");

    const defaultImage = '/static/images/walrusicon.png';
    let userAvatar = user['img_src'];
    if (!userAvatar) userAvatar = defaultImage;

    const username = user['username'];

    newDiv.innerHTML = `<img src="${userAvatar}" alt="${username}'s avatar" class="avatar" /><b>${username}</b>`;

    userList.append(newDiv);
}

/*
	removeOnlineUser
  	    Parameters:	    user - a user's information in JSON format
	    Return Value:   none
	Description:
        Removes the online user div associated with the passed in user's username
*/
function removeOnlineUser(user) {
    const userList = document.getElementsByClassName('user-list-item');
    let divToDelete;
    for (let u of userList) {
        console.log(`Want to delete ${user.username}     -       Iterating: ${u.innerText}`)
        if (u.innerText === user['username'])
            divToDelete = u;
    }
    if (divToDelete) {
        console.log(`Deleting: ${divToDelete.innerText}`);
        divToDelete.remove();
    }
}

function removeAllUsers() {
    const userList = document.getElementsByClassName('user-list-item');
    for (let u of userList) {
         u.remove();
    }
}

// called when the page loads to get the online users
function getOnlineUsers() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            console.log(`response: ${this.response}`);
            const users = JSON.parse(this.response);
            for (let user of users) {
                console.log(`Adding User ${user.username}`);
                addOnlineUser(user);
            }
        }
    };
    request.open("GET", "/online-users");
    request.send();
}

function initializePage() {
    // get_chat_history();`
    console.log("Initializing...");
    getOnlineUsers();
}




const testMessages = [];
let i;
for (i = 0; i < 5; i++) {
    const messageType = 'chatMessage';
    const username = `User${i}`;
    const message = `Lorem ipsum`;
    const payload = {
        messageType: messageType,
        username: username,
        comment: message
    }
    testMessages.push(payload);
    // console.log(payload);
}

// for (let tm of testMessages) addMessage(tm);`

function addTestMessage() {
    let chatview = document.getElementsByClassName('chat-view')[0];
    const newDiv = document.createElement('div');
    newDiv.classList.add("chat-message");

    const messageType = 'chatMessage';
    const username = `User${i}`;
    const message = `Lorem ipsum`;
    const payload = {
        messageType: messageType,
        username: username,
        comment: message
    }

    newDiv.innerHTML = ("<b>" + payload['username'] + "</b>: " + payload["comment"] + "<br/>");
    chatview.prepend(newDiv);
    addOnlineUser({username: username})
    i++;
}
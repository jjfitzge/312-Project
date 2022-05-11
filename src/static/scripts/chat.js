// const socket = new WebSocket('ws://' + window.location.host + '/websocket');

function sendMessage() {
    const chatBox = document.getElementById("chat-comment");
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
// socket.onmessage = function (ws_message) {
//     const message = JSON.parse(ws_message.data);
//     const messageType = message.messageType

//     switch (messageType) {
//         case 'chatMessage':
//             addMessage(message);
//             break;
//         case 'webRTC-offer':
//             webRTCConnection.setRemoteDescription(new RTCSessionDescription(message.offer));
//             webRTCConnection.createAnswer().then(answer => {
//                 webRTCConnection.setLocalDescription(answer);
//                 socket.send(JSON.stringify({'messageType': 'webRTC-answer', 'answer': answer}));
//             });
//             break;
//         case 'webRTC-answer':
//             webRTCConnection.setRemoteDescription(new RTCSessionDescription(message.answer));
//             break;
//         case 'webRTC-candidate':
//             webRTCConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
//             break;
//         default:
//             console.log("received an invalid WS messageType");
//     }
// }

console.log("Adding messages")

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

for (let tm of testMessages) addMessage(tm);

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
    i++;
}
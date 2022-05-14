const socket = new WebSocket('ws://' + window.location.host + '/websocket');

let webRTCConnection;

socket.onmessage = function (ws_message) {
    const message = JSON.parse(ws_message.data);
    const messageType = message.messageType

    switch (messageType) {
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

function startVideo() {
    const constraints = {video: true, audio: true};
    navigator.mediaDevices.getUserMedia(constraints).then((myStream) => {
        const elem = document.getElementById("myVideo");
        elem.srcObject = myStream;

        // Use Google's public STUN server
        const iceConfig = {
            'iceServers': [{'url': 'stun:stun2.1.google.com:19302'}]
        };

        // create a WebRTC connection object
        webRTCConnection = new RTCPeerConnection(iceConfig);

        // add your local stream to the connection
        webRTCConnection.addStream(myStream);

        // when a remote stream is added, display it on the page
        webRTCConnection.onaddstream = function (data) {
            const remoteVideo = document.getElementById('otherVideo');
            remoteVideo.srcObject = data.stream;
        };

        // called when an ice candidate needs to be sent to the peer
        webRTCConnection.onicecandidate = function (data) {
            socket.send(JSON.stringify({'messageType': 'webRTC-candidate', 'candidate': data.candidate}));
        };
    })
}


function connectWebRTC() {
    const input = document.getElementById("send-to-user");
    const toUser = input.value;
    input.value = "";
    input.focus();
    // console.log("toUser", toUser);
    // create and send an offer
    webRTCConnection.createOffer().then(webRTCOffer => {
        if(toUser != "") {
            // console.log("Sending: ", (JSON.stringify({'messageType': 'webRTC-offer', 'offer': webRTCOffer, 'toUser':toUser})))
            socket.send(JSON.stringify({'messageType': 'webRTC-offer', 'offer': webRTCOffer, 'toUser':toUser}));
            webRTCConnection.setLocalDescription(webRTCOffer);
        }
    });

}
var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {
    socket.emit('connected', {data: 'New user'});
});

socket.on('connected', function(data) {
    console.log("Connected user " + data)
});


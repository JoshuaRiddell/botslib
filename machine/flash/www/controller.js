var websocket;

var connection_status;
var pad1x;
var pad1y;
var pad2x;
var pad2y;

window.addEventListener("load", init, false);
window.addEventListener('beforeunload', function (e) {
    websocket.close();
});

window.addEventListener("gamepadconnected", function(e) {
    console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
        e.gamepad.index, e.gamepad.id,
        e.gamepad.buttons.length, e.gamepad.axes.length);
    window.setInterval(gamepad_poll, 200);
});


window.addEventListener("gamepaddisconnected", function(e) {
    console.log("Gamepad disconnected.");
});

function gamepad_poll() {
    var gamepad = navigator.getGamepads()[0];

    var val1x = Math.round(gamepad.axes[0] * 100) / 100;
    var val1y = Math.round(gamepad.axes[1] * 100) / 100;
    var val2x = Math.round(gamepad.axes[2] * 100) / 100;
    var val2y = Math.round(gamepad.axes[3] * 100) / 100;

    pad1x.innerHTML = val1x;
    pad1y.innerHTML = val1y;
    pad2x.innerHTML = val2x;
    pad2y.innerHTML = val2y;

    console.log(val1x);
    console.log(val1y);
    console.log(val2x);
    console.log(val2y);

    socket_send(
        "a" + val1x + "," + val1y + "," + val2x + "," + val2y
    );
}
// 
function init() {
    connection_status = document.getElementById("connection_status");
    pad1x = document.getElementById("pad1x");
    pad1y = document.getElementById("pad1y");
    pad2x = document.getElementById("pad2x");
    pad2y = document.getElementById("pad2y");
    
    attach_socket();
}

function attach_socket() {
    var wsUri = "ws://" + window.location.hostname + "/controller";
    update_connection_status("Connection to " + wsUri + " ...")
    websocket = new WebSocket(wsUri);
    websocket.onopen = function (evt) { onOpen(evt) };
    websocket.onclose = function (evt) { onClose(evt) };
    websocket.onmessage = function (evt) { onMessage(evt) };
    websocket.onerror = function (evt) { onError(evt) };
}

function onOpen(evt) {
    update_connection_status("<strong>-- CONNECTED --</strong>");
}

function onClose(evt) {
    update_connection_status("<strong>-- DISCONNECTED --</strong>");
}

function onMessage(evt) {
    update_connection_status('MSG FROM SERVER : <span style="color: blue;">' + evt.data + '</span>');
}

function onError(evt) {
    update_connection_status('ERROR : <span style="color: red;">' + evt.data + '</span>');
}

function socket_send(msg) {
    websocket.send(msg);
}

function update_connection_status(s) {
    var pre = document.createElement("p");
    pre.style.wordWrap = "break-word";
    pre.innerHTML = s;
    connection_status.appendChild(pre);
}

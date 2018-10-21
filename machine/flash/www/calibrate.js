window.addEventListener("load", init, false);

var websocket;

var connection_status;
var degrees_slider;
var degrees_readout;
var id_input;
var id_readout;
var write_button;
var write_readout;

function init() {
    connection_status = document.getElementById("connection_status");
    degrees_slider = document.getElementById("degrees_slider");
    degrees_readout = document.getElementById("degrees_readout");
    id_input = document.getElementById("id_input");
    id_readout = document.getElementById("id_readout");
    write_button = document.getElementById("write_button");
    write_readout = document.getElementById("write_readout");

    degrees_slider.oninput = function () {
        degrees_readout.innerHTML = this.value;
        socket_send("a" + this.value);
    }

    id_input.oninput = function () {
        id_readout.innerHTML = this.value;
        socket_send("i" + this.value);
    }

    write_button.onclick = function () {
        write_readout.innerHTML = "Sent!";
        socket_send("w");
    }

    attach_socket();
}

function attach_socket() {
    var wsUri = "ws://" + window.location.hostname + "/calibrate";
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
    if (evt.data[0] == 'a') {
        var angle = parseFloat(evt.data.slice(1))
        degrees_slider.value = angle;
        degrees_readout.innerHTML = angle;
    } else {
        update_connection_status('MSG FROM SERVER : <span style="color: blue;">' + evt.data + '</span>');
    }
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

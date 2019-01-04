var websocket;

var connection_status;
var pad1x;
var pad1y;
var pad2x;
var pad2y;
var trig_l;
var trig_r;

var z_height_slider;
var z_height_readout;

var walk_status;

window.addEventListener("load", init, false);
window.addEventListener('beforeunload', function (e) {
    websocket.close();
});

window.addEventListener("gamepadconnected", function(e) {
    console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
        e.gamepad.index, e.gamepad.id,
        e.gamepad.buttons.length, e.gamepad.axes.length);
    window.setInterval(gamepad_poll, 100);
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
    var val3 = Math.round(gamepad.buttons[6].value * 100) / 100;
    var val4 = Math.round(gamepad.buttons[7].value * 100) / 100;

    pad1x.innerHTML = val1x;
    pad1y.innerHTML = val1y;
    pad2x.innerHTML = val2x;
    pad2y.innerHTML = val2y;
    trig_l.innerHTML = val3;
    trig_r.innerHTML = val4;

    if (Math.abs(val1y) < 0.55) {
        val1y = 0;
    }

    if (Math.abs(val1x) < 0.1) {
        val1x = 0;
    }
    if (Math.abs(val2x) < 0.1) {
        val2x = 0;
    }
    if (Math.abs(val2y) < 0.1) {
        val2y = 0;
    }

    socket_send(
        "a" + val1x + "," + val1y + "," + z_height_slider.value + "," + val2x + "," + val2y + "," + val3 + "," + val4
    );
}

function init() {
    connection_status = document.getElementById("connection_status");
    pad1x = document.getElementById("pad1x");
    pad1y = document.getElementById("pad1y");
    pad2x = document.getElementById("pad2x");
    pad2y = document.getElementById("pad2y");
    trig_l = document.getElementById("trig_l");
    trig_r = document.getElementById("trig_r");

    walk_status = document.getElementById("walk_status");
    var start_button = document.getElementById("start_button");
    var stop_button = document.getElementById("stop_button");
    
    start_button.onclick = function () {
        walk_status.innerHTML = "On";
        socket_send("s");
    }

    stop_button.onclick = function () {
        walk_status.innerHTML = "Off";
        socket_send("x");
    }

    attach_socket();

    var connect_button = document.getElementById("connect_button");
    var disconnect_button = document.getElementById("disconnect_button");

    connect_button.onclick = function() {
        if (websocket.readyState == 3) {
            attach_socket();
        }
    }

    disconnect_button.onclick = function() {
        if (websocket.readyState == 1) {
            websocket.close();
        }
    }

    z_height_slider = document.getElementById("z_height_slider");
    z_height_readout = document.getElementById("z_height_readout");

    z_height_slider.oninput = function () {
        z_height_readout.innerHTML = this.value;
    }
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
    if (websocket.readyState == 1) {
        websocket.send(msg);
    }
}

function update_connection_status(s) {
    connection_status.innerHTML = s;
}

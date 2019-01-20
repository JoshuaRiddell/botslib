// websocket to the bot
var websocket;

// html elements
var connection_status;
var pad1x;
var pad1y;
var pad2x;
var pad2y;
var trig_l;
var trig_r;

// controller scaling
var x_scale;
var y_scale;
var yaw_scale;

// z height slider html elements
var z_height_slider;
var z_height_readout;

// walk parameter inputs
var dt;
var move_time;
var step_time;
var step_period;
var step_thresh_readout;
var step_thresh_slider;
var scaling_factor_readout;
var scaling_factor_slider;

// walk status readout html element
var walk_status;

// run init function on load
window.addEventListener("load", init, false);

// close bot websocket on close
window.addEventListener('beforeunload', function (e) {
    websocket.close();
});

// set gamepad polling when gamepad is detected
window.addEventListener("gamepadconnected", function(e) {
    console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
        e.gamepad.index, e.gamepad.id,
        e.gamepad.buttons.length, e.gamepad.axes.length);
    window.setInterval(gamepad_poll, 150);
});

// let the programmer know when the gamepad is not detected
window.addEventListener("gamepaddisconnected", function(e) {
    console.log("Gamepad disconnected.");
});

// when the gamepad is polled, send every value to the bot
function gamepad_poll() {
    var gamepad = navigator.getGamepads()[0];

    // get each gamepad axis
    var val1x = Math.round(gamepad.axes[0] * 100) / 100;
    var val1y = Math.round(gamepad.axes[1] * 100) / 100;
    var val2x = Math.round(gamepad.axes[2] * 100) / 100;
    var val2y = Math.round(gamepad.axes[3] * 100) / 100;
    var val3 = Math.round(gamepad.buttons[6].value * 100) / 100;
    var val4 = Math.round(gamepad.buttons[7].value * 100) / 100;

    // update value readouts on webpage
    pad1x.innerHTML = val1x;
    pad1y.innerHTML = val1y;
    pad2x.innerHTML = val2x;
    pad2y.innerHTML = val2y;
    trig_l.innerHTML = val3;
    trig_r.innerHTML = val4;

    // implement a dead range (larger for y axis since controller is broken)
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
    
    val1x = val1x * x_scale.value;
    val1y = val1y * y_scale.value;
    val2x = val2x * yaw_scale.value;

    // send data as csv over websocket
    socket_send(
        "a" + val1x + "," + val1y + "," + z_height_slider.value + "," + val2x + "," + val2y + "," + val3 + "," + val4
    );
}

function init() {
    // get html elements
    connection_status = document.getElementById("connection_status");
    pad1x = document.getElementById("pad1x");
    pad1y = document.getElementById("pad1y");
    pad2x = document.getElementById("pad2x");
    pad2y = document.getElementById("pad2y");
    trig_l = document.getElementById("trig_l");
    trig_r = document.getElementById("trig_r");

    x_scale = document.getElementById("x_scale");
    y_scale = document.getElementById("y_scale");
    yaw_scale = document.getElementById("yaw_scale");

    walk_status = document.getElementById("walk_status");
    var start_button = document.getElementById("start_button");
    var stop_button = document.getElementById("stop_button");
    
    // when walk start button is pressed indicate and send start command
    start_button.onclick = function () {
        walk_status.innerHTML = "On";

        socket_send("s" + dt.value + ","
                    + move_time.value + ","
                    + step_time.value + ","
                    + step_period.value + ","
                    + step_thresh_slider.value + ","
                    + scaling_factor_slider.value);
    }

    // when walk stop button is pressed indicate and send stop command
    stop_button.onclick = function () {
        walk_status.innerHTML = "Off";
        socket_send("x");
    }

    // connect to bot
    attach_socket();

    // implement socket connect and disconnect buttons
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

    // when z height slider is changed, change the height indicator.
    // sending of this value is handled in the gamepad callback
    z_height_slider = document.getElementById("z_height_slider");
    z_height_readout = document.getElementById("z_height_readout");

    z_height_slider.oninput = function () {
        z_height_readout.innerHTML = this.value;
    }

    // walking parameter inputs
    dt = document.getElementById("dt");
    move_time = document.getElementById("move_time");
    step_time = document.getElementById("step_time");
    step_period = document.getElementById("step_period");
    step_thresh_readout = document.getElementById("step_thresh_readout");
    step_thresh_slider = document.getElementById("step_thresh_slider");
    scaling_factor_readout = document.getElementById("scaling_factor_readout");
    scaling_factor_slider = document.getElementById("scaling_factor_slider");

    step_thresh_slider.oninput = function () {
        step_thresh_readout.innerHTML = this.value;
    }

    scaling_factor_slider.oninput = function () {
        scaling_factor_readout.innerHTML = this.value;
    }
}

// attaches socket and registers callbacks
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

// sends to socket if socket is connected
function socket_send(msg) {
    if (websocket.readyState == 1) {
        websocket.send(msg);
    }
}

// updates the connection status text box
function update_connection_status(s) {
    connection_status.innerHTML = s;
}

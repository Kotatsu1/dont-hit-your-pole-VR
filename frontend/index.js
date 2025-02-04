let newPos = { x: 0, y: 0, z: 0 };

async function setPosition() {
  await window.pywebview.api.VR.set_pole_offset(newPos);
}

function updateValue(axis, delta) {
  newPos[axis] += delta;
  document.getElementById(axis + "-value").textContent =
    newPos[axis].toFixed(6);
  setPosition();
}

async function saveConfig() {
  await window.pywebview.api.VR.save_config();
}

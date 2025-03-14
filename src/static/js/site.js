function refreshMap() {
    showLoaders();
    fetch('/new_map', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.statuscode == 200) {
            document.getElementById("error").style.display = 'none';
            document.getElementById("error").innerHTML = "";
            hideLoaders();
            window.location.reload();
        } else {
            document.getElementById("error").style.display = 'block';
            document.getElementById("error").innerHTML = data.message;
            hideLoaders();
        }
    })
    .catch(error => console.error('Error:', error));
    
};

async function getPlottedDevices(){
    var count = "Loading...";
    document.getElementById("total-devices-count").innerHTML = "Loading...";
    try{
        count = document.querySelectorAll('#map .awesome-marker').length / 2;
    }catch{
        count = -1;
    }
    document.getElementById("total-devices-count").innerHTML = count;
}

function hideLoaders(){
    document.getElementById("loader-container").style.display = 'none';
}

function showLoaders(){
    document.getElementById("loader-container").style.display = 'flex';
}

window.onload = function() {
    getPlottedDevices();
}
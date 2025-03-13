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

function hideLoaders(){
    document.getElementById("loader").style.display = 'none';
}

function showLoaders(){
    document.getElementById("loader").style.display = 'block';
}
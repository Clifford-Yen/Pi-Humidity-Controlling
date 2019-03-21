function turnAircon(operation) {
    blockUsersInteraction()
    var xhttp = new XMLHttpRequest()
    xhttp.onreadystatechange = function() {
        /* XMLHttpRequest.readyState == 4 shows that the state is DONE, 
        which means the operation is complete.
        And XMLHttpRequest.status == 200 means the request is successful.
        See: https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/readyState
        and https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/status */
        if (this.readyState == 4 && this.status == 200) {
            // JSON.parse would convert the (dictionary format) string into a dictionary
            var result = JSON.parse(xhttp.responseText)
            if (result.result == 'success') {
                // alert("The operation '"+operation+"' is completed.")
            } else {
                alert("The operation '"+operation+"' is not completed. Something wrong.")
            }
            restoreUsersInteraction()
        }
    }
    xhttp.open('POST', "/turnAircon", true)
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhttp.send('operation='+operation)
}

function blockUsersInteraction() {
    var overlay = document.getElementById('overlay')
    overlay.className = 'progress'
}

function restoreUsersInteraction() {
    var overlay = document.getElementById('overlay')
    overlay.classList.remove('progress')
}
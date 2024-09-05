document.getElementById('start-sound-test-btn').addEventListener('click', function () {
    // Start the sound test by calling the backend
    fetch('/start_sound_test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Test completed") {
            showResults(data.responses);
        } else {
            showPopup(data.frequency, data.decibel);
        }
    });
});

// Show the popup with frequency and decibel values
function showPopup(frequency, decibel) {
    document.getElementById('freq').innerText = frequency;
    document.getElementById('db').innerText = decibel;
    document.getElementById('popup').style.display = 'block';
    setTimeout(function() {
        document.getElementById('popup').style.display = 'none';
        document.getElementById('response-section').style.display = 'block';
    }, 2000);  // Hide popup after sound plays (2 seconds)
}

// Send user response and play next sound
document.getElementById('yes-btn').addEventListener('click', function () {
    sendUserResponse('Yes');
});

document.getElementById('no-btn').addEventListener('click', function () {
    sendUserResponse('No');
});

function sendUserResponse(response) {
    fetch('/user_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ response: response })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Test completed") {
            showResults(data.responses);
        } else {
            showPopup(data.frequency, data.decibel);
        }
    });
}

// Show the final test results
function showResults(responses) {
    document.getElementById('response-section').style.display = 'none';
    document.getElementById('popup').style.display = 'none';
    document.getElementById('result').style.display = 'block';
    document.getElementById('responses').innerText = JSON.stringify(responses, null, 2);
}

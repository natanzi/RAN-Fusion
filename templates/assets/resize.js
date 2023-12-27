document.addEventListener('DOMContentLoaded', function() {
    // Existing code for resizing...

    // Add event listener for form submission
    var form = document.getElementById('traffic-form'); // Replace with your actual form ID
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Collect data from form
        var data = {
            bitrate_range: [
                parseInt(document.getElementById('minBitrate').value, 10), 
                parseInt(document.getElementById('maxBitrate').value, 10)
            ],
            jitter: parseFloat(document.getElementById('jitter').value),
            delay: parseFloat(document.getElementById('delay').value),
            packet_loss_rate: parseFloat(document.getElementById('packetLossRate').value)
        };

        // Validate data
        if (validatePayload(data)) {
            // Send POST request if validation passes
            sendPostRequest('/update_gaming_traffic', data);
        } else {
            // Handle validation errors
            console.error('Validation failed');
            // Display an error message to the user
        }
    });
});

function validatePayload(data) {
    // Validation logic here...
    return isValidType(data.bitrate_range, 'object') && // Arrays are 'object' type in JS
           Array.isArray(data.bitrate_range) &&
           data.bitrate_range.length === 2 &&
           isValidType(data.bitrate_range[0], 'number') &&
           isValidType(data.bitrate_range[1], 'number') &&
           isValidType(data.jitter, ['number']) &&
           isValidType(data.delay, ['number']) &&
           isValidType(data.packet_loss_rate, ['number']);
}

function isValidType(value, expectedType) {
    if (Array.isArray(expectedType)) {
        return expectedType.includes(typeof value);
    } else {
        return typeof value === expectedType;
    }
}

function sendPostRequest(url, data) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        // Handle success response
    })
    .catch((error) => {
        console.error('Error:', error);
        // Handle errors
    });
}
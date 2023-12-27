document.addEventListener('DOMContentLoaded', function() {
    // Existing code for resizing...
    var isResizing = false;

    var mapContainer = document.getElementById('map-container');
    var tabsContainer = document.getElementById('tabs-container');
    var divider = document.getElementById('divider');

    divider.addEventListener('mousedown', function(e) {
        isResizing = true;
    });

    document.addEventListener('mousemove', function(e) {
        if (!isResizing) {
            return;
        }

        var containerOffsetTop = mapContainer.offsetTop;
        var newHeight = e.clientY - containerOffsetTop;

        mapContainer.style.height = newHeight + 'px';
        tabsContainer.style.height = 'calc(100vh - ' + newHeight + 'px - 30px)';
    });

    document.addEventListener('mouseup', function(e) {
        isResizing = false;
    });

    // Add event listener for form submission
    var form = document.getElementById('traffic-form'); // Ensure this ID matches your form
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
            // Ideally, display an error message to the user in the UI
        }
    });
});

function validatePayload(data) {
    // Validation logic here...
    return isValidType(data.bitrate_range, 'object') &&
           Array.isArray(data.bitrate_range) &&
           data.bitrate_range.length === 2 &&
           isValidType(data.bitrate_range[0], 'number') &&
           isValidType(data.bitrate_range[1], 'number') &&
           isValidType(data.jitter, 'number') &&
           isValidType(data.delay, 'number') &&
           isValidType(data.packet_loss_rate, 'number');
}

function isValidType(value, expectedType) {
    return typeof value === expectedType;
}

function sendPostRequest(url, data) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        // Handle success response
        // Ideally, inform the user of success in the UI
    })
    .catch((error) => {
        console.error('Error:', error);
        // Handle errors
        // Ideally, display an error message to the user in the UI
    });
}
document.addEventListener('DOMContentLoaded', function() {
    // Resize Handlers
    var isResizing = false;
    var mapContainer = document.getElementById('map-container');
    var tabsContainer = document.getElementById('tabs-container');
    var divider = document.getElementById('divider');  // Assuming there's a divider element for resizing

    divider.addEventListener('mousedown', function(e) {
        isResizing = true;
    });

    document.addEventListener('mousemove', function(e) {
        if (!isResizing) return;
        var containerOffsetTop = mapContainer.offsetTop;
        var newHeight = e.clientY - containerOffsetTop;

        mapContainer.style.height = newHeight + 'px';
        tabsContainer.style.height = 'calc(100vh - ' + newHeight + 'px)';
    });

    document.addEventListener('mouseup', function() {
        isResizing = false;
    });

    // Form Submission Handling
    var forms = ['voiceTrafficForm', 'videoTrafficForm', 'gamingTrafficForm', 'iotTrafficForm', 'dataTrafficForm'];
    forms.forEach(function(formId) {
        var form = document.getElementById(formId);
        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                var data = serializeForm(formId);

                try {
                    validatePayload(data);
                    sendPostRequest('/update_' + formId.replace('TrafficForm', ''), data);
                } catch (error) {
                    console.error('Validation Error:', error);
                    // Handle validation error (e.g., show error message to user)
                }
            });
        }
    });
});

function serializeForm(formId) {
    var form = document.getElementById(formId);
    var elements = form.elements;
    var data = {};

    for (var i = 0; i < elements.length; i++) {
        if (elements[i].type !== 'submit') {
            var value = elements[i].value;
            // Parse numerical values appropriately
            if (elements[i].type === 'number') {
                value = elements[i].step && elements[i].step.indexOf('.') >= 0 ? parseFloat(value) : parseInt(value, 10);
            }
            data[elements[i].id] = value;
        }
    }

    // Adjust the data structure for specific forms to match server expectations
    switch(formId) {
        case 'gamingTrafficForm':
            data = {
                bitrate_range: [data.gaming_min_bitrate, data.gaming_max_bitrate],
                jitter: data.gaming_jitter,
                delay: data.gaming_delay,
                packet_loss_rate: data.gaming_packet_loss_rate
            };
            break;
        // Add similar adjustments for other forms if necessary
    }

    return data;
}

function validatePayload(data) {
    // Implement specific validation logic here
    // Throw an error if validation fails
    // Example: if (!data.bitrate_range) throw new Error("Bitrate range is required.");
    // Return nothing if validation passes
}

function sendPostRequest(endpoint, data) {
    fetch(`http://127.0.0.1:5000/${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        alert('Traffic updated successfully');
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating traffic');
    });
}

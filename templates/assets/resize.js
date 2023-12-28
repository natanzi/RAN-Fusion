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
            // Parsing numerical values as floats for precision
            data[elements[i].id] = elements[i].type === 'number' ? parseFloat(elements[i].value) : elements[i].value;
        }
    }

    // Adjusting the data structure based on the formId
    switch(formId) {
        case 'gamingTrafficForm':
            data = {
                bitrate_range: [data.gaming_min_bitrate, data.gaming_max_bitrate],
                jitter: data.gaming_jitter,
                delay: data.gaming_delay,
                packet_loss_rate: data.gaming_packet_loss_rate
            };
            break;
        case 'videoTrafficForm':
            data = {
                num_streams_range: [data.video_min_streams, data.video_max_streams],
                stream_bitrate_range: [data.video_min_bitrate, data.video_max_bitrate],
                jitter: data.video_jitter,
                delay: data.video_delay,
                packet_loss_rate: data.video_packet_loss_rate
            };
            break;
        case 'voiceTrafficForm':
            data = {
                bitrate_range: [data.voice_min_bitrate, data.voice_max_bitrate],
                jitter: data.voice_jitter,
                delay: data.voice_delay,
                packet_loss_rate: data.voice_packet_loss_rate
            };
            break;
        case 'iotTrafficForm':
            data = {
                packet_size_range: [data.iot_min_packet_size, data.iot_max_packet_size],
                interval_range: [data.iot_min_interval, data.iot_max_interval],
                jitter: data.iot_jitter,
                delay: data.iot_delay,
                packet_loss_rate: data.iot_packet_loss_rate
            };
            break;
        case 'dataTrafficForm':
            data = {
                bitrate_range: [data.data_min_bitrate, data.data_max_bitrate],
                interval_range: [data.data_min_interval, data.data_max_interval],
                jitter: data.data_jitter,
                delay: data.data_delay,
                packet_loss_rate: data.data_packet_loss_rate
            };
            break;
        // Add any additional form adjustments here if needed
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

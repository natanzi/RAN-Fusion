// formValidation.js

// Function to validate numerical input within a range
function validateRangeInput(value, min, max) {
    return value >= min && value <= max;
}

// Function to validate form data
function validateFormData(formId) {
    let isValid = true;
    let errorMessage = '';

    if (formId === 'voiceTrafficForm') {
        const minBitrate = parseInt(document.getElementById('voice_min_bitrate').value, 10);
        const maxBitrate = parseInt(document.getElementById('voice_max_bitrate').value, 10);
        if (!validateRangeInput(minBitrate, 8, 16) || !validateRangeInput(maxBitrate, 8, 16)) {
            errorMessage = 'Bitrate for voice traffic must be between 8 and 16 kbps.';
            isValid = false;
        }
    } else if (formId === 'videoTrafficForm') {
        const minStreams = parseInt(document.getElementById('video_min_streams').value, 10);
        const maxStreams = parseInt(document.getElementById('video_max_streams').value, 10);
        const minBitrate = parseInt(document.getElementById('video_min_bitrate').value, 10);
        const maxBitrate = parseInt(document.getElementById('video_max_bitrate').value, 10);
        if (!validateRangeInput(minStreams, 1, 5) || !validateRangeInput(maxStreams, 1, 5) ||
            !validateRangeInput(minBitrate, 3, 8) || !validateRangeInput(maxBitrate, 3, 8)) {
            errorMessage = 'Number of streams must be between 1 and 5, and bitrate must be between 3 and 8 Mbps.';
            isValid = false;
        }
    } else if (formId === 'gamingTrafficForm') {
        const minBitrate = parseInt(document.getElementById('gaming_min_bitrate').value, 10);
        const maxBitrate = parseInt(document.getElementById('gaming_max_bitrate').value, 10);
        if (!validateRangeInput(minBitrate, 30, 70) || !validateRangeInput(maxBitrate, 30, 70)) {
            errorMessage = 'Bitrate for gaming traffic must be between 30 and 70 Mbps.';
            isValid = false;
        }
    } else if (formId === 'iotTrafficForm') {
        const minPacketSize = parseInt(document.getElementById('iot_min_packet_size').value, 10);
        const maxPacketSize = parseInt(document.getElementById('iot_max_packet_size').value, 10);
        const minInterval = parseInt(document.getElementById('iot_min_interval').value, 10);
        const maxInterval = parseInt(document.getElementById('iot_max_interval').value, 10);
        if (!validateRangeInput(minPacketSize, 20, 1500) || !validateRangeInput(maxPacketSize, 20, 1500)) {
            errorMessage = 'Packet size for IoT traffic must be between 20 and 1500 bytes.';
            isValid = false;
        }
        if (!validateRangeInput(minInterval, 1, 60) || !validateRangeInput(maxInterval, 1, 60)) {
            errorMessage += '\nInterval for IoT traffic must be between 1 and 60 seconds.';
            isValid = false;
        }
    }
    
    // Add validation for Data form
    if (formId === 'dataTrafficForm') {
        const minBitrate = parseInt(document.getElementById('data_min_bitrate').value, 10);
        const maxBitrate = parseInt(document.getElementById('data_max_bitrate').value, 10);
        const minInterval = parseInt(document.getElementById('data_min_interval').value, 10);
        const maxInterval = parseInt(document.getElementById('data_max_interval').value, 10);
        if (!validateRangeInput(minBitrate, 10, 1000) || !validateRangeInput(maxBitrate, 10, 1000)) {
            errorMessage = 'Bitrate for data traffic must be between 10 and 1000 Mbps.';
            isValid = false;
        }
        if (!validateRangeInput(minInterval, 1, 60) || !validateRangeInput(maxInterval, 1, 60)) {
            errorMessage += '\nInterval for data traffic must be between 1 and 60 seconds.';
            isValid = false;
        }
    }
    
function serializeFormData(form) {
        const formData = new FormData(form);
        const data = {};
    
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
    
        return data;
    }  
    return { isValid, errorMessage };
}

// Function to handle form submission
function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formId = form.id;
    const validation = validateFormData(formId);

    if (!validation.isValid) {
        alert(validation.errorMessage);
        return;
    }

    const data = serializeFormData(form);

    fetch(`/update_${formId.replace('Form', '')}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        alert('Traffic updated successfully');
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('Error updating traffic');
    });
}

    // Replace '/your-endpoint' with the correct server endpoint
    fetch(`/update_${formId.replace('Form', '')}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        alert('Traffic updated successfully');
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('Error updating traffic');
    });


// Attach event listeners to forms
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
});
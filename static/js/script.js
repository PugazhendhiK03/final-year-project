// Recording controls
$(document).ready(function() {
    let recording = false;

    $('#record-btn').click(function() {
        if (!recording) {
            $.get("/start_recording_all", function(data) {
                console.log(data);
                $('#record-btn').text('Stop Recording');
                recording = true;
            });
        } else {
            $.get("/stop_recording_all", function(data) {
                console.log(data);
                $('#record-btn').text('Start Recording');
                recording = false;
            });
        }
    });
});

$(document).ready(function() {
    $('#upload-form').submit(function(event) {
        event.preventDefault();

        let formData = new FormData();
        let fileInput = $('#image-upload')[0].files[0];
        formData.append('image', fileInput);

        $.ajax({
            type: 'POST',
            url: '/upload_image',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                console.log(response);
            },
            error: function(xhr, status, error) {
                console.error(xhr.responseText);
            }
        });
    });

    // Event handler for turning off face recognition
    $('#turn-off-face-recognition').click(function() {
        $.get("/turn_off_face_recognition", function(data) {
            console.log(data);
            alert('Face recognition turned off.');
        });
    });
});

// Object detection turn off
document.getElementById("turn-off-object-detection").addEventListener("click", function() {
    fetch('/turn_off_object_detection', {
        method: 'GET',
    })
    .then(response => {
        if (response.ok) {
            console.log('Object detection turned off.');
        } else {
            console.error('Failed to turn off object detection.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

// Image preview functionality
function previewImage(event) {
    var input = event.target;
    var preview = document.getElementById('image-preview');

    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = 'block'; // Show the image preview
        };

        reader.readAsDataURL(input.files[0]);
    }
}

// Navbar functionality
$(document).ready(function() {
    // Initially hide library and alerts sections
    $('#library').hide();
    $('#alerts').hide();

    // Show livemonitor section
    $('#livemonitor').show();

    // Event listener for 'fa-photo-film' option (Library)
    $('.fa-photo-film').parent().click(function() {
        // Hide livemonitor and show library
        $('#livemonitor').hide();
        $('#library').show();

        // Hide alerts if visible
        $('#alerts').hide();
    });

    // Event listener for 'fa-bell' option (Alerts)
    $('.fa-bell').parent().click(function() {
        // Show alerts and hide other sections
        $('#alerts').show();
        $('#livemonitor').hide();
        $('#library').hide();
    });

    // Event listener for 'fa-video' option (Live Monitor)
    $('.fa-video').parent().click(function() {
        // Show livemonitor and hide other sections
        $('#livemonitor').show();
        $('#library').hide();
        $('#alerts').hide();
    });

    // Recording controls
    $('#record-btn').click(function() {
        if (!recording) {
            $.get("/start_recording_all", function(data) {
                console.log(data);
                $('#record-btn').text('Stop Recording');
                $('#status').text(data.status); // Show recording status
                recording = true;
            });
        } else {
            $.get("/stop_recording_all", function(data) {
                console.log(data);
                $('#record-btn').text('Start Recording');
                $('#status').text(data.status); // Show recording status
                recording = false;
            });
        }
    });
});



// JavaScript for user dropdown
document.addEventListener("DOMContentLoaded", function() {
    const userDropdown = document.querySelector(".user-dropdown");
    const dropdownContent = document.querySelector(".dropdown-content");

    // Toggle dropdown content on user icon click
    userDropdown.addEventListener("click", function(event) {
        event.stopPropagation(); // Prevent the click event from bubbling up

        // Toggle display of dropdown content
        dropdownContent.style.display = dropdownContent.style.display === "block" ? "none" : "block";
    });

    // Close dropdown content when clicking outside of it
    document.addEventListener("click", function(event) {
        if (!userDropdown.contains(event.target)) {
            dropdownContent.style.display = "none";
        }
    });
});




// alerts images
$(document).ready(function() {
    // Reload matched faces images
    $('#reload-matched-faces').click(function() {
        $('#matched-faces-images').empty(); // Clear existing images
        fetchMatchedFaces(); // Fetch and load matched faces again
    });

    // Reload object images
    $('#reload-object-images').click(function() {
        $('#object-images').empty(); // Clear existing images
        fetchObjectImages(); // Fetch and load object images again
    });

    // Function to fetch and load matched faces
function fetchMatchedFaces() {
    $.get("/get_matched_faces", function(data) {
        var matchedFacesImages = data.images;
        var matchedFacesContainer = $('#matched-faces-images');

        matchedFacesImages.forEach(function(image) {
            var imageUrl = `/static/matched_faces/${image}`;
            var imgElement = `<div class="image-container"><img src="${imageUrl}" alt="Matched Face" class="full-screen-image" data-url="${imageUrl}"><div class="filename">${image}</div></div>`;
            matchedFacesContainer.append(imgElement);
        });
    });
}

// Function to fetch and load object images
function fetchObjectImages() {
    $.get("/get_object_images", function(data) {
        var objectImages = data.images;
        var objectImagesContainer = $('#object-images');

        objectImages.forEach(function(image) {
            var imageUrl = `/static/object_images/${image}`;
            var imgElement = `<div class="image-container"><img src="${imageUrl}" alt="Object Image" class="full-screen-image" data-url="${imageUrl}"><div class="filename">${image}</div></div>`;
            objectImagesContainer.append(imgElement);
        });
    });
}

// Initial load of matched faces and object images
fetchMatchedFaces();
fetchObjectImages();

// Event listener for full screen images
$(document).on('click', '.full-screen-image', function() {
    var imageUrl = $(this).data('url');
    openFullScreenImage(imageUrl);
});

// Function to open image in full screen
function openFullScreenImage(imageUrl) {
    var modal = $('<div class="full-screen-modal">').appendTo('body');
    var image = $('<img class="full-screen-image-modal">').attr('src', imageUrl).appendTo(modal);

    // Close modal on click
    modal.click(function() {
        modal.remove();
    });
}




//  library playback
$(document).ready(function() {
    // Function to fetch and load recorded videos
    function fetchRecordedVideos() {
        $.get("/get_recorded_videos", function(data) {
            var recordedVideos = data.videos;
            var recordedVideosList = $('#recorded-videos-list');

            recordedVideos.forEach(function(video) {
                var videoUrl = `/recordings/${video}`;
                var videoElement = `<div class="video-item" data-url="${videoUrl}">${video}</div>`;
                recordedVideosList.append(videoElement);
            });
        })
        .done(function() {
            console.log('Recorded videos loaded successfully.');

            // Attach click event handler to video items (using event delegation)
            $('#recorded-videos-list').on('click', '.video-item', function() {
                var videoUrl = $(this).data('url');
                openVideoModal(videoUrl);
            });
        })
        .fail(function(xhr, status, error) {
            console.error('Failed to load recorded videos:', error);
        });
    }

    // Initial load of recorded videos
    fetchRecordedVideos();

    // Function to open video in modal popup
function openVideoModal(videoUrl) {
    var videoPlayer = document.getElementById('videoPlayer');
    var source = document.createElement('source');
    source.setAttribute('src', videoUrl);
    source.setAttribute('type', 'video/mp4');
    videoPlayer.appendChild(source);

    var modal = document.getElementById('videoModal');
    modal.style.display = 'block';

    var span = document.getElementsByClassName('close')[0];
    span.onclick = function() {
        modal.style.display = 'none';
        videoPlayer.pause();
        videoPlayer.removeChild(source); // Remove the video source when closing
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
            videoPlayer.pause();
            videoPlayer.removeChild(source); // Remove the video source when closing
        }
    }
}


    // Reload recorded videos
    $('#reload-recorded-videos').click(function() {
        $('#recorded-videos-list').empty(); // Clear existing videos
        fetchRecordedVideos(); // Fetch and load recorded videos again
    });
});



})

const searchForm = $("#search-form");
const searchFormInput = searchForm.find("input");
const info = $(".info");

let mediaRecorder;
let chunks = [];

// Check if the browser supports MediaRecorder
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    console.log("Your Browser supports MediaRecorder");

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = function(e) {
                chunks.push(e.data);
            }

            mediaRecorder.onstop = function() {
                const blob = new Blob(chunks, { type: 'audio/webm' });
                const recordedFile = new File([blob], 'audiorecord.webm')
                let data = new FormData();
                data.append('recorded_audio', recordedFile)
                const url = document.getElementById("submit-url").href;

                $.ajax({
                   url:url,
                   method: "POST",
                   data:data,
                   dataType: "json",
                   beforeSend: function () {
                     $("#loading-spinner").show();
                   },
                   success: function (response) {
                       $("#loading-spinner").hide();
                       if (response.success) {
                           window.location.href = `${response.url}`;
                       } else {
                           console.log("An Error occurred");
                       }
                   },
                   error: function (error) {
                       console.error(error);
                   },
                    cache:false,
                    processData: false,
                    contentType:false,
                });
            }
        })
        .catch(function(err) {
            console.error("Error accessing microphone:", err);
        });

    // Add click event listener to start recording
    $("#start-recording").on("click", function() {
        chunks = [];
        if (mediaRecorder) {
            mediaRecorder.start();
            console.log("Recording started");

            $("#start-recording").hide(); // Hide start recording button
            $("#stop-recording").show(); // Show stop recording button
        }
    });

    // Add click event listener to stop recording
    $("#stop-recording").on("click", function() {
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
            console.log("Recording stopped");
            $("#start-recording").show(); // Show start recording button
            $("#stop-recording").hide(); // Hide stop recording button
        }
    });

    info.text('Click the microphone to start recording.');

} else {
    console.log("Your Browser does not support MediaRecorder");
    info.text("Your Browser does not support MediaRecorder");
}


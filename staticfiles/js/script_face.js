$(document).ready(function(){
    var video = document.getElementById('video');
    var canvas = document.getElementById('overlay');
    var context = canvas.getContext('2d');
    var captureButton = $('#capture-btn');

    navigator.mediaDevices.getUserMedia({ video: true })
    .then(function(stream) {
        video.srcObject = stream;
        video.play();
        detectFace();
    })
    .catch(function(err) {
        console.error('Kamera yoqilishda xatolik:', err);
    });

    function detectFace() {
        var videoWidth = video.videoWidth;
        var videoHeight = video.videoHeight;
        canvas.width = videoWidth;
        canvas.height = videoHeight;
        context.clearRect(0, 0, canvas.width, canvas.height);

        var tracker = new tracking.ObjectTracker('face');
        tracker.setInitialScale(4);
        tracker.setStepSize(2);
        tracker.setEdgesDensity(0.1);
        tracking.track('#video', tracker, { camera: true });

        tracker.on('track', function(event) {
            context.clearRect(0, 0, canvas.width, canvas.height);
            event.data.forEach(function(rect) {
                context.strokeStyle = '#a64ceb';
                context.lineWidth = 2;
                context.strokeRect(rect.x, rect.y, rect.width, rect.height);
            });
        });
    }

    captureButton.click(function() {
        var imgData = canvas.toDataURL('image/jpeg');

        // Backendga tasvirni yuborish
        $.ajax({
            type: 'POST',
            url: '/capture/',
            data: { image: imgData },
            success: function(response) {
                console.log('Tasvir backendga yuborildi:', response);
                alert('Tasvir backendga muvaffaqiyatli yuborildi va saqlandi.');
            },
            error: function(xhr, status, error) {
                console.error('Xatolik:', error);
                alert('Xatolik yuz berdi. Iltimos, qayta urinib ko\'ring.');
            }
        });
    });
});

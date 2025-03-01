var captureButton = $('#capture-btn');
var video = document.getElementById('video');
var canvas = document.createElement('canvas');  // Yangi canvas yaratamiz
var context = canvas.getContext('2d');

captureButton.click(function() {
    // Canvas o‘lchamini video o‘lchamiga moslashtiramiz
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    var imgData = canvas.toDataURL('image/jpeg');  // ✅ Video'dan rasm olamiz

    console.log("📡 Yuborilayotgan tasvir:", imgData.substring(0, 100));  // 🔍 JSON'da to‘g‘ri ekanligini tekshirish

    // Backendga tasvirni yuborish
    $.ajax({
        type: 'POST',
        url: '/uz/users/login/faceid/',  // ✅ To‘g‘ri endpoint ekanligini tekshiring
        data: JSON.stringify({ image: imgData.split(',')[1] }),  // ✅ Base64 formatda faqat rasm qismi yuboriladi
        contentType: 'application/json',
        dataType: 'json',
        success: function(response) {
            console.log("✅ Serverdan javob:", response);
            if (response.success) {
                alert("✅ Face ID orqali tizimga kirdingiz!");
                window.location.href = response.url;
            } else {
                alert(response.message);
            }
        },
        error: function(xhr, status, error) {
            console.error('❌ Xatolik:', xhr.responseText);
            alert('Xatolik yuz berdi: ' + error);
        }
    });
});

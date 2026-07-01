// Profiles photo preview script
function previewImage(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            let previewImg = document.getElementById('previewImg');
            if (!previewImg) {
                const previewContainer = document.querySelector('.text-center');
                const defaultIcon = previewContainer.querySelector('.rounded-circle');
                if (defaultIcon) {
                    defaultIcon.remove();
                }
                const img = document.createElement('img');
                img.id = 'previewImg';
                img.src = e.target.result;
                img.alt = 'Preview';
                img.className = 'rounded-circle mb-3';
                img.style.width = '200px';
                img.style.height = '200px';
                img.style.object_fit = 'cover';
                previewContainer.insertBefore(img, previewContainer.firstChild);
            } else {
                previewImg.src = e.target.result;
            }
        };
        reader.readAsDataURL(file);
    }
}

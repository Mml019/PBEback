window.addEventListener("load", function () {
    const images = document.querySelectorAll(".img-fluid");
    
    images.forEach(img => {
        const file = img.dataset.file.toLowerCase();
        let extension = file.split(".").pop() //file.split(".")[1]
        
        if (extension) {
            img.src = `/static/img/filetype-${extension}.svg`;
        }else{
            img.src = `/static/img/file.svg`;
        }
    })

});

window.addEventListener("load", function () {
    const images = document.querySelectorAll(".img-fluid");
    console.log(images)
    images.forEach(img => {
        const file = img.dataset.file.toLowerCase();
        let extension = file.split(".")[1]// or .split(".").pop()

        if (extension) {
            img.src = `/static/img/filetype-${extension}.svg`;
        }else{
            img.src = `/static/img/file.svg`;
        }
    })

});

// function quizImageAdd(name, num){

//     var extension = name.toLowerCase().split(".")[1]

//     switch(extension){
//         case "csv":  src = `/static/img/filetype-${extension}.svg`;break
//         case "xlsx" :
//         case "xls":  src = `/static/img/filetype-exe.svg`; break;
//         default: src = `/static/img/file.svg`;
//     }
//     return src
// }

// document.addEventListener("DOMContentLoaded", function () {
//     const images = document.querySelectorAll(".img-fluid");

//     images.forEach((img) => {
//         const fileName = img.dataset.file;
//         img.src = quizImageAdd(fileName);
//     });

// });

// window.addEventListener(onload, function () {
//     const images = document.querySelectorAll("quiz-img");
//     console.log(images)

//     images.forEach(img => {
//         const fileName = img.dataset.file;
//         img.src = quizImageAdd(fileName);
//     });

// });


function quizImageAdd(name){
    var extension = name.split(".")[1]
    img = document.getElementById("quiz_img")
    if (extension == "csv" || extension =="exe"){
        src = `img/filetype-${extension}.svg`
        img.src = src
    }
}
window.addEventListener("load", function () {
    // load images to quizzes but first get quizzes

    const images = document.querySelectorAll(".img-fluid");
    const deleteModal = document.getElementById('deleteModal'); // Replace with your modal's ID

    // change to false when the modal is showed
    deleteModal.addEventListener('show.bs.modal', (e) => {
        deleteModal.ariaHidden = false
    });

    // Change to true when the  modal is hidden
    deleteModal.addEventListener('hidden.bs.modal', (e) => {
        deleteModal.ariaHidden = true
    });

    images.forEach(img => {
        const file = img.dataset.file.toLowerCase();
        let extension = file.split(".").pop() //file.split(".")[1]

        if (extension) {
            img.src = `/static/img/filetype-${extension}.svg`;
        } else {
            img.src = `/static/img/file.svg`;
        }
    })
});

const fileInput = document.getElementById("file-input");
const import_accept = document.getElementById("import-but-accept");
const importForm = document.getElementById("import-form")

fileInput.addEventListener('change', () => {
    import_accept.disabled = (fileInput.files.length === 0);
});

fileInput.addEventListener('click', ()=>{
    import_accept.disabled = (fileInput.value == null)
})

importForm.addEventListener("submit", () => {
    import_accept.disabled = true;
    import_accept.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status"></span>
        Importando...
    `;
});

// To show the object in data-* params to the delete modal
const deleteButtons = document.querySelectorAll(".delete-button")
deleteButtons.forEach((deletebutton) => {
    deletebutton.addEventListener(('click'), () => {
        let quizId = deletebutton.dataset.id
        let quizFile = deletebutton.dataset.file
        let quizUrl = deletebutton.dataset.url

        // Add into delete modal action and text dinamically
        document.getElementById('delete-modal-form').action = quizUrl
        document.getElementById('delete-modal-text').innerText = `¿Seguro que quiere borrar el cuestionario ${quizId}.${quizFile}?`
    })
});




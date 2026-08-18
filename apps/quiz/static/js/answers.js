const exportAnswerForm = document.getElementById('export_answers')
const butAnswerExport = document.getElementById('export_answers_btn')

exportAnswerForm.addEventListener('submit', ()=>{
    butAnswerExport.disabled = false
    butAnswerExport.innerHTML =`<span class="spinner-border spinner-border-sm" role="status"></span>Importando...`;
})

exportAnswerForm.addEventListener("submit", () => {
    butAnswerExport.disabled = true;
    butAnswerExport.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status"></span>
        Exportando...
    `;
});

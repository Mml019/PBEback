const exportAnswerForm = document.getElementById('export_answers')
const butAnswerExport = document.getElementById('export_answers_btn')
const loadingOverlay = document.getElementById('loading-overlay')

exportAnswerForm.addEventListener('submit', async (e)=>{
    e.preventDefault()
    butAnswerExport.disabled = true
    const originText = butAnswerExport.innerText 
    butAnswerExport.innerHTML =`<span class="spinner-border spinner-border-sm" role="status"></span>Exportando...`;
    // delete to show modal
    loadingOverlay.classList.remove('d-none'); 
    try {
        const params = new URLSearchParams(new FormData(exportAnswerForm));
        // const url = e.target.action + "?" +new URLSearchParams(new FormData(e.target)) 
        const url = `${exportAnswerForm.action}?${params.toString()}`;
        console.log(url)
        // To launch the request asnwers/donwload
        const response = await fetch(url, {method:"GET"})
        if (!response.ok) {
            butAnswerExport.disabled = false;
            butAnswerExport.innerText = originText;
            return alert(`Error exportación.${response.error}`)
        }

        const blob = await response.blob();
        
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
           
        const format = params.get("format");
        const type = params.get("type");
        // To donwload the archive
        var fileExportName = 'answers';
        console.log(fileExportName)
        a.download = `${fileExportName}`;
        a.click();
        a.remove();
        
    } catch (error) {
        console.log(error)
        return alert(`Error exportación. Error:${error}`)
    }finally{
        butAnswerExport.disabled = false;
        butAnswerExport.innerText = originText;
        loadingOverlay.classList.add('d-none');        
    }
});
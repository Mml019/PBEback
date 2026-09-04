const trows = document.querySelectorAll('#users tbody tr')

trows.forEach((row) => {
    row.addEventListener('click', (e) =>{
        console.log(`me ha clicado en fila${row} + ${e.target}`)
    })
});

const exportUserForm = document.getElementById('export_users')
const btnUserExport = document.getElementById('export_users_btn')
const loadingOverlay = document.getElementById('loading-overlay')

exportUserForm.addEventListener('submit', async (e)=>{
    e.preventDefault()
    btnUserExport.disabled = true
    const originText = btnUserExport.innerText 
    btnUserExport.innerHTML =`<span class="spinner-border spinner-border-sm" role="status"></span>Exportando...`;
    // delete to show modal
    // loadingOverlay.classList.remove('d-none'); 
    try {
        const params = new URLSearchParams(new FormData(exportUserForm));
        // const url = e.target.action + "?" +new URLSearchParams(new FormData(e.target)) 
        const url = `${exportUserForm.action}?${params.toString()}`;
        console.log(url)
        // To launch the request asnwers/donwload
        const response = await fetch(url, {method:"GET"})
        if (!response.ok) {
            btnUserExport.disabled = false;
            btnUserExport.innerText = originText;
            return alert(`Error exportación.${response.error}`)
        }

        const blob = await response.blob();
        
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
           
        const format = params.get("format");
        const type = params.get("type");
        // To donwload the archive
        var fileExportName = `users_${type === "complex" ? "complex" : "simple"}.${format === "csv" ? "csv" : "xlsx"}`;
        console.log(fileExportName)
        a.download = `${fileExportName}`;
        a.click();
        a.remove();
        
    } catch (error) {
        console.log(error)
        return alert(`Error exportación. Error:${error}`)
    }finally{
        btnUserExport.disabled = false;
        btnUserExport.innerText = originText;
        // loadingOverlay.classList.add('d-none');        
    }
});

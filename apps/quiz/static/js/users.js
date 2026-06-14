const trows = document.querySelectorAll('#users tbody tr')

trows.forEach((row) => {
    row.addEventListener('click', (e) =>{
        
    })
});

const exportUserForm = document.getElementById('export_users')
const butUserExport = document.getElementById('export_users_btn')

exportUserForm.addEventListener('submit', async (e)=>{
    butUserExport.disabled = true
    butUserExport.innerHTML =`<span class="spinner-border spinner-border-sm" role="status"></span>Exportando...`;

    try {
        const url = e.target.action + "?" +new URLSearchParams(new FormData(e.target)) 
        response = await fecth(url)

        if (!response.ok) {
            btn.disabled = false;
            btn.innerText = "Exportar";
            return alert(`Error exportación.`)
        }

        const blob = await response.blob();

        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `${response.resultName}`;
        a.click();

        btn.disabled = false;
        btn.innerText = "Exportar";
        
    } catch (error) {
        return alert(`Error exportación. Error:${error}`)
    }

})
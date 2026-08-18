const trows = document.querySelectorAll('#users tbody tr')

trows.forEach((row) => {
    row.addEventListener('click', (e) =>{
        console.log(`me ha clicado en fila${row} + ${e.target}`)
    })
});

const exportUserForm = document.getElementById('export_users')
const btnUserExport = document.getElementById('export_users_btn')
const loadingOverlay = document.getElementById('loading-overlay')
const formBut = document.getElementById('form-but')
const exportFormUserBut = document.getElementById('form-but-user')

exportUserForm.addEventListener('submit', async (e)=>{
    e.preventDefault()
    btnUserExport.disabled = true
    const originText = btnUserExport.innerText 
    btnUserExport.innerHTML =`<span class="spinner-border spinner-border-sm" role="status"></span>Exportando...`;
    // delete to show modal
    loadingOverlay.classList.remove('d-none'); 
    console.log("spinner y true y d-none")
    try {
        const params = new URLSearchParams(new FormData(exportUserForm));
        // const response = await fetch(`${exportUserForm.action}?${params}`);
        const url = e.target.action + "?" +new URLSearchParams(new FormData(e.target)) 
        console.log(url)
        const response = await fetch(url, {method:"GET"})
        // console.log(`response ${response.body}${response.json}`)
        // if (!response.ok) {
        //     btnUserExport.disabled = false;
        //     btnUserExport.innerText = originText;
        //     return alert(`Error exportación.${response.error}`)
        // }

        const blob = await response.blob();
        
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        // Before donwload stablish nameresults file
        console.log(params)
        const fileExportName=""
        if (params[type]=="complex"){
            fileExportName="users_complex"
        }else{
            fileExportName="users_simple"
        }
        if (params[format]=="csv"){
            fileExportName+=".csv"
        }else{
            fileExportName+=".xlsx"
        }
        const type = params.get("type");
        //Hacerlo así:
        // const format = params.get("format");

        // const fileExportName = `users_${type === "complex" ? "complex" : "simple"}.${format === "csv" ? "csv" : "xlsx"}`;
        // const fileType = params.get("type") === "complex"
        //     ? "complex"
        //     : "simple";

        // const extension = params.get("format") === "csv"
        //     ? "csv"
        //     : "xlsx";

        // const fileExportName = `users_${fileType}.${extension}`;
        //         a.download = `${response.resultName}`;
        //         a.click();
        //         a.remove()

        // btnUserExport.disabled = false;
        // btnUserExport.innerText = "Exportar";
        
    } catch (error) {
        console.log(error)
        return alert(`Error exportación. Error:${error}`)
    }finally{
        btnUserExport.disabled = false;
        btnUserExport.innerText = "Exportar";
        console.log("finally execute")
        loadingOverlay.classList.add('d-none');
        //   btnUserExport.disabled = false;
        // btnUserExport.innerText = "Exportar";
        
    }
});

// formBut.addEventListener('submit', async (e)=>{
//     exportFormUserBut.disabled=true;
//     console.log("disabled" + exportFormUserBut)
//     try{
//         const params = new URLSearchParams(new FormData(formBut));
//         console.log(`${formBut.action}?${params}`)
//         const response = await fetch(`${formBut.action}?${params}`);
//         exportFormUserBut.disabled = false;
//         exportFormUserBut.innerText = "Exportar";
//     }catch(e){

//     }finally{
//         // exportFormUserBut.disabled = false;
//         // exportFormUserBut.innerText = "Exportar";
//         // console.log("finally execute")
//     }
// });
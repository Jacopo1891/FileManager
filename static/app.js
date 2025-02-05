async function fetchFiles() {
    let response = await fetch('/files/');
    let data = await response.json();
    let fileTableBody = document.querySelector('#fileTable tbody');
    fileTableBody.innerHTML = '';

    data.files.forEach(file => {
        let row = document.createElement('tr');
        row.innerHTML = `
            <td>${file.name}</td>
            <td>${file.uploadDate}</td>
            <td>
                <input type="text" id="rename-${file.name}" placeholder="Nuovo nome">
                <button class="rename-btn" onclick="renameFile('${file.name}')">✏️ Rinomina</button>
                <button class="delete-btn" onclick="deleteFile('${file.name}')">❌ Elimina</button>
            </td>
        `;
        fileTableBody.appendChild(row);
    });
}

async function renameFile(oldName) {
    let newName = document.getElementById(`rename-${oldName}`).value.trim();
    if (!newName) {
        alert("Inserisci un nuovo nome valido!");
        return;
    }
    
    let response = await fetch(`/rename/${oldName}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_name: newName })
    });

    let result = await response.json();
    alert(result.message);
    fetchFiles();
}

async function uploadFile(event) {
    event.preventDefault();
    let formData = new FormData(event.target);
    let response = await fetch('/upload/', { method: 'POST', body: formData });
    let result = await response.json();
    alert(result.message);
    event.target.reset();  // Resetta il modulo per rimuovere i file selezionati
    fetchFiles();
}

async function deleteFile(filename) {
    let response = await fetch(`/delete/${filename}`, { method: 'DELETE' });
    let result = await response.json();
    alert(result.message);
    fetchFiles();
}

window.onload = fetchFiles;
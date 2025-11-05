const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("fileInput");
const compressBtn = document.getElementById("compressBtn");
const decompressBtn = document.getElementById("decompressBtn");
const status = document.getElementById("status");
const spinner = document.getElementById("spinner");
const themeToggle = document.getElementById("themeToggle");
const recentList = document.getElementById("recentList");

let selectedFile = null;
let recentFiles = [];

// Format bytes
function formatSize(bytes) {
    if (bytes < 1024) return bytes + " B";
    else if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + " KB";
    else return (bytes / (1024 * 1024)).toFixed(2) + " MB";
}

// Drag & drop events
dropZone.addEventListener("click", () => fileInput.click());
dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("dragover"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    selectedFile = e.dataTransfer.files[0];
    dropZone.querySelector("p").textContent = `Selected: ${selectedFile.name}`;
});

// File input change
fileInput.addEventListener("change", () => {
    selectedFile = fileInput.files[0];
    dropZone.querySelector("p").textContent = `Selected: ${selectedFile.name}`;
});

// Upload function
function uploadFile(endpoint) {
    if (!selectedFile) { alert("Please select a file first!"); return; }

    const formData = new FormData();
    formData.append("file", selectedFile);

    spinner.style.display = "block";
    status.textContent = "Processing...";
    status.className = "";
    status.style.opacity = 1;

    fetch(`/${endpoint}`, { method: "POST", body: formData })
    .then(res => res.json())
    .then(data => {
        spinner.style.display = "none";
        if (data.error) {
            status.textContent = "❌ " + data.error;
            status.classList.add("error", "fade-in");
            return;
        }

        const filenameParts = selectedFile.name.split(".");
        let ext = filenameParts.length > 1 ? "." + filenameParts.pop() : "";
        let baseName = filenameParts.join(".");
        let downloadName = endpoint === "compress" 
            ? baseName + "_compressed" + ext 
            : baseName + "_decompressed" + ext;

        const downloadLink = `<a href="${data.file_url}" download="${downloadName}">${downloadName}</a>`;

        let info = "";
        if (endpoint === "compress") {
            const ratioPercent = ((1 - data.compressed_size / data.original_size) * 100).toFixed(2) + "%";
            info = `Original: ${formatSize(data.original_size)}<br>
                    Compressed: ${formatSize(data.compressed_size)}<br>
                    Compression saved: ${ratioPercent}`;
        } else {
            const ratioPercent = ((data.decompressed_size / data.original_size - 1) * 100).toFixed(2) + "%";
            info = `Compressed: ${formatSize(data.original_size)}<br>
                    Decompressed: ${formatSize(data.decompressed_size)}<br>
                    Size increase: ${ratioPercent}`;
        }

        status.innerHTML = `✅ Done!<br>${info}<br>${downloadLink}`;
        status.classList.add("success");
        status.classList.remove("fade-in");
        void status.offsetWidth;
        status.classList.add("fade-in");

        // Add to recent files
        recentFiles.unshift(downloadLink); // newest first
        recentList.innerHTML = recentFiles.join("<br>");
    })
    .catch(err => {
        spinner.style.display = "none";
        console.error(err);
        status.textContent = "❌ Error!";
        status.classList.add("error", "fade-in");
    });
}

// Button events
compressBtn.addEventListener("click", () => uploadFile("compress"));
decompressBtn.addEventListener("click", () => uploadFile("decompress"));

// Dark mode toggle
themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
    themeToggle.textContent = document.body.classList.contains("dark-mode") ? "☀️" : "🌙";
});

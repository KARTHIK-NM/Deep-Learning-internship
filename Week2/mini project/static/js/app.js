/**
 * PhytoScan AI — Frontend Controller
 * Handles drag-and-drop, camera capture, sample gallery, REST inference,
 * animated gauge/confidence charts, and treatment tabs.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dropzone = document.getElementById('dropzone');
    const leafFileInput = document.getElementById('leafFileInput');
    const browseFilesBtn = document.getElementById('browseFilesBtn');
    const dropzoneEmpty = document.getElementById('dropzoneEmpty');
    const dropzonePreview = document.getElementById('dropzonePreview');
    const previewImage = document.getElementById('previewImage');
    const clearPreviewBtn = document.getElementById('clearPreviewBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');

    // Camera elements
    const openCameraBtn = document.getElementById('openCameraBtn');
    const cameraModal = document.getElementById('cameraModal');
    const cameraVideo = document.getElementById('cameraVideo');
    const cameraCanvas = document.getElementById('cameraCanvas');
    const capturePhotoBtn = document.getElementById('capturePhotoBtn');
    const closeCameraBtn = document.getElementById('closeCameraBtn');

    // Sample gallery
    const samplesContainer = document.getElementById('samplesContainer');
    const sampleCountBadge = document.getElementById('sampleCountBadge');

    // Results elements
    const resultsPlaceholder = document.getElementById('resultsPlaceholder');
    const resultsPanel = document.getElementById('resultsPanel');
    const verdictBanner = document.getElementById('verdictBanner');
    const verdictBadge = document.getElementById('verdictBadge');
    const severityBadge = document.getElementById('severityBadge');
    const diagnosedCondition = document.getElementById('diagnosedCondition');
    const diagnosedCrop = document.getElementById('diagnosedCrop');
    const scientificName = document.getElementById('scientificName');
    const confidenceGauge = document.getElementById('confidenceGauge');
    const confidencePercentage = document.getElementById('confidencePercentage');
    const metaPathogen = document.getElementById('metaPathogen');
    const metaSeverity = document.getElementById('metaSeverity');
    const metaLatency = document.getElementById('metaLatency');
    const conditionSummary = document.getElementById('conditionSummary');
    const probListContainer = document.getElementById('probListContainer');

    // Treatment tabs & lists
    const symptomsList = document.getElementById('symptomsList');
    const organicList = document.getElementById('organicList');
    const chemicalList = document.getElementById('chemicalList');
    const preventionList = document.getElementById('preventionList');
    const tabButtons = document.querySelectorAll('.tab-btn');

    // Model modal
    const modelInfoBtn = document.getElementById('modelInfoBtn');
    const modelModal = document.getElementById('modelModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const statAccuracy = document.getElementById('statAccuracy');
    const statTop3 = document.getElementById('statTop3');
    const statLoss = document.getElementById('statLoss');
    const statParams = document.getElementById('statParams');

    // State
    let selectedFile = null;
    let selectedSampleFilename = null;
    let cameraStream = null;

    // -------------------------------------------------------------
    // File Upload & Drag-and-Drop
    // -------------------------------------------------------------
    browseFilesBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        leafFileInput.click();
    });

    dropzone.addEventListener('click', () => {
        if (!selectedFile && !selectedSampleFilename) {
            leafFileInput.click();
        }
    });

    leafFileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            handleSelectedFile(e.target.files[0]);
        }
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('drag-over');
        });
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        if (dt.files && dt.files[0]) {
            handleSelectedFile(dt.files[0]);
        }
    });

    function handleSelectedFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please select a valid image file (JPG, PNG, WEBP).');
            return;
        }
        selectedFile = file;
        selectedSampleFilename = null;

        // Reset any active sample highlight
        document.querySelectorAll('.sample-thumb-card').forEach(c => c.classList.remove('active-sample'));

        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            dropzoneEmpty.classList.add('hidden');
            dropzonePreview.classList.remove('hidden');
            analyzeBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    clearPreviewBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetUploadState();
    });

    function resetUploadState() {
        selectedFile = null;
        selectedSampleFilename = null;
        leafFileInput.value = '';
        previewImage.src = '';
        dropzonePreview.classList.add('hidden');
        dropzoneEmpty.classList.remove('hidden');
        analyzeBtn.disabled = true;
        document.querySelectorAll('.sample-thumb-card').forEach(c => c.classList.remove('active-sample'));
    }

    // -------------------------------------------------------------
    // Camera Support
    // -------------------------------------------------------------
    openCameraBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        try {
            cameraStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
            });
            cameraVideo.srcObject = cameraStream;
            cameraModal.classList.remove('hidden');
        } catch (err) {
            alert('Camera access could not be initialized: ' + err.message);
        }
    });

    closeCameraBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        stopCamera();
    });

    capturePhotoBtn.addEventListener('click', () => {
        if (!cameraStream) return;
        const width = cameraVideo.videoWidth || 640;
        const height = cameraVideo.videoHeight || 480;
        cameraCanvas.width = width;
        cameraCanvas.height = height;
        const ctx = cameraCanvas.getContext('2d');
        ctx.drawImage(cameraVideo, 0, 0, width, height);

        cameraCanvas.toBlob((blob) => {
            const capturedFile = new File([blob], "camera_leaf_snapshot.jpg", { type: "image/jpeg" });
            handleSelectedFile(capturedFile);
            stopCamera();
        }, 'image/jpeg', 0.95);
    });

    function stopCamera() {
        if (cameraStream) {
            cameraStream.getTracks().forEach(track => track.stop());
            cameraStream = null;
        }
        cameraModal.classList.add('hidden');
    }

    // -------------------------------------------------------------
    // Sample Quick-Test Gallery
    // -------------------------------------------------------------
    async function loadSamples() {
        try {
            const res = await fetch('/api/samples');
            const data = await res.json();
            if (data.success && data.samples.length > 0) {
                sampleCountBadge.textContent = `${data.samples.length} Field Samples`;
                samplesContainer.innerHTML = '';

                data.samples.forEach(sample => {
                    const card = document.createElement('div');
                    card.className = 'sample-thumb-card';
                    card.dataset.filename = sample.filename;

                    const isHealthy = sample.class_id.toLowerCase().includes('healthy');
                    const cleanCrop = sample.label.split(' - ')[0];
                    const cleanCondition = sample.label.split(' - ')[1] || 'Sample';

                    card.innerHTML = `
                        <img class="sample-thumb-img" src="/static/samples/${sample.filename}" alt="${sample.label}" loading="lazy">
                        <div class="sample-thumb-meta">
                            <span class="sample-thumb-name">${cleanCrop}</span>
                            <span class="sample-thumb-tag ${isHealthy ? '' : 'tag-disease'}">
                                ${isHealthy ? '● Healthy' : '● ' + cleanCondition}
                            </span>
                        </div>
                    `;

                    card.addEventListener('click', () => {
                        selectSample(sample, card);
                    });

                    samplesContainer.appendChild(card);
                });
            } else {
                samplesContainer.innerHTML = '<p class="sample-hint">No test samples found in library.</p>';
            }
        } catch (err) {
            console.error('Error loading samples:', err);
            samplesContainer.innerHTML = '<p class="sample-hint">Could not connect to sample library.</p>';
        }
    }

    function selectSample(sample, cardElement) {
        document.querySelectorAll('.sample-thumb-card').forEach(c => c.classList.remove('active-sample'));
        cardElement.classList.add('active-sample');

        selectedSampleFilename = sample.filename;
        selectedFile = null;
        leafFileInput.value = '';

        previewImage.src = `/static/samples/${sample.filename}`;
        dropzoneEmpty.classList.add('hidden');
        dropzonePreview.classList.remove('hidden');
        analyzeBtn.disabled = false;

        // Auto-run inference for instant feedback
        runInference();
    }

    // -------------------------------------------------------------
    // Inference Action
    // -------------------------------------------------------------
    analyzeBtn.addEventListener('click', runInference);

    async function runInference() {
        if (!selectedFile && !selectedSampleFilename) return;

        const startTime = performance.now();
        setLoadingState(true);

        try {
            let response;
            if (selectedFile) {
                const formData = new FormData();
                formData.append('file', selectedFile);
                response = await fetch('/api/predict', {
                    method: 'POST',
                    body: formData
                });
            } else if (selectedSampleFilename) {
                response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sample_filename: selectedSampleFilename })
                });
            }

            const result = await response.json();
            const latency = Math.round(performance.now() - startTime);

            if (result.success) {
                displayDiagnosisResults(result, latency);
            } else {
                alert('Diagnostic error: ' + (result.error || 'Unknown error occurred.'));
            }
        } catch (err) {
            console.error('Inference error:', err);
            alert('Failed to connect to AI inference server: ' + err.message);
        } finally {
            setLoadingState(false);
        }
    }

    function setLoadingState(isLoading) {
        const btnText = analyzeBtn.querySelector('.btn-text');
        const btnSpinner = analyzeBtn.querySelector('.btn-spinner');
        if (isLoading) {
            analyzeBtn.disabled = true;
            btnText.classList.add('hidden');
            btnSpinner.classList.remove('hidden');
        } else {
            analyzeBtn.disabled = false;
            btnText.classList.remove('hidden');
            btnSpinner.classList.add('hidden');
        }
    }

    // -------------------------------------------------------------
    // Render Diagnosis Results
    // -------------------------------------------------------------
    function displayDiagnosisResults(data, latencyMs) {
        const p = data.prediction;

        resultsPlaceholder.classList.add('hidden');
        resultsPanel.classList.remove('hidden');

        // Verdict styling & badges
        const isHealthy = p.is_healthy;
        verdictBadge.textContent = isHealthy ? 'HEALTHY FOLIAGE' : 'DISEASE DETECTED';
        verdictBadge.className = `verdict-badge ${isHealthy ? 'badge-healthy' : ''}`;

        severityBadge.textContent = isHealthy ? 'Optimal Plant Health' : `${p.severity} Severity Threat`;
        severityBadge.style.color = p.color_code;

        diagnosedCondition.textContent = p.condition;
        diagnosedCrop.textContent = p.crop;
        scientificName.textContent = p.scientific_name;

        // Circular confidence gauge
        animateConfidenceGauge(p.confidence, p.color_code);

        // Metadata
        metaPathogen.textContent = p.pathogen_type;
        metaSeverity.textContent = isHealthy ? 'None (Clean Specimen)' : `${p.severity} Pathological Risk`;
        metaLatency.textContent = `${latencyMs} ms`;
        conditionSummary.textContent = p.description;

        // Top 5 Probabilities
        renderProbabilities(data.top_predictions);

        // Treatment & Care lists
        populateList(symptomsList, p.symptoms);
        populateList(organicList, p.organic_treatment);
        populateList(chemicalList, p.chemical_treatment);
        populateList(preventionList, p.prevention);

        // Smooth scroll on mobile
        if (window.innerWidth < 1024) {
            resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    function animateConfidenceGauge(targetConfidence, colorCode) {
        let current = 0;
        const duration = 900;
        const startTime = performance.now();

        function updateGauge(time) {
            const elapsed = time - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease-out cubic
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            current = (targetConfidence * easeProgress).toFixed(1);

            confidencePercentage.textContent = `${current}%`;
            const angle = (current / 100) * 360;
            confidenceGauge.style.background = `conic-gradient(${colorCode} ${angle}deg, rgba(255, 255, 255, 0.08) ${angle}deg)`;

            if (progress < 1) {
                requestAnimationFrame(updateGauge);
            }
        }
        requestAnimationFrame(updateGauge);
    }

    function renderProbabilities(predictions) {
        probListContainer.innerHTML = '';
        predictions.forEach((item, index) => {
            const row = document.createElement('div');
            row.className = 'prob-item';

            row.innerHTML = `
                <div class="prob-info">
                    <span class="prob-name">${item.label}</span>
                    <span class="prob-score" style="color: ${item.color_code}">${item.confidence}%</span>
                </div>
                <div class="prob-track">
                    <div class="prob-bar" id="bar-${index}" style="background: ${item.color_code}"></div>
                </div>
            `;
            probListContainer.appendChild(row);

            // Animate bar width
            setTimeout(() => {
                const bar = document.getElementById(`bar-${index}`);
                if (bar) bar.style.width = `${item.confidence}%`;
            }, 60);
        });
    }

    function populateList(ulElement, items) {
        ulElement.innerHTML = '';
        if (!items || items.length === 0) {
            ulElement.innerHTML = '<li>No specific items documented for this category.</li>';
            return;
        }
        items.forEach(text => {
            const li = document.createElement('li');
            li.textContent = text;
            ulElement.appendChild(li);
        });
    }

    // -------------------------------------------------------------
    // Treatment Tabs
    // -------------------------------------------------------------
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            tabButtons.forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const targetId = btn.dataset.tab;
            const targetPane = document.getElementById(targetId);
            if (targetPane) targetPane.classList.add('active');
        });
    });

    // -------------------------------------------------------------
    // Model Architecture & Stats Modal
    // -------------------------------------------------------------
    modelInfoBtn.addEventListener('click', async () => {
        modelModal.classList.remove('hidden');
        try {
            const res = await fetch('/api/model-info');
            const data = await res.json();
            if (data.success && data.metrics) {
                const m = data.metrics;
                statAccuracy.textContent = m.final_accuracy ? `${(m.final_accuracy * 100).toFixed(1)}%` : '--';
                statTop3.textContent = m.final_top3_accuracy ? `${(m.final_top3_accuracy * 100).toFixed(1)}%` : '--';
                statLoss.textContent = m.final_loss ? m.final_loss.toFixed(3) : '--';
                if (m.parameters) {
                    statParams.textContent = `${(m.parameters / 1000000).toFixed(2)} M`;
                }
            }
        } catch (e) {
            console.error('Error fetching model stats:', e);
        }
    });

    closeModalBtn.addEventListener('click', () => {
        modelModal.classList.add('hidden');
    });

    modelModal.addEventListener('click', (e) => {
        if (e.target === modelModal) modelModal.classList.add('hidden');
    });

    // -------------------------------------------------------------
    // Encyclopedia Strip Loader
    // -------------------------------------------------------------
    function renderEncyclopedia() {
        const grid = document.getElementById('diseaseGrid');
        if (!grid) return;

        const catalog = [
            { crop: "Apple", title: "Apple Scab / Black Rot", desc: "Causes frog-eye lesions, fruit rot, and bark cankers; requires early sanitation and copper/sulfur sprays." },
            { crop: "Apple", title: "Healthy Foliage", desc: "Clean deep-green foliage, free of spots or powdery mildew; signifies optimal photosynthetic capacity." },
            { crop: "Corn (Maize)", title: "Common Rust", desc: "Airborne Puccinia sorghi produces brick-red powdery spore pustules disrupting grain yield." },
            { crop: "Corn (Maize)", title: "Healthy Foliage", desc: "Strong parallel venation and vigorous leaf blades supporting maximum ear development." },
            { crop: "Bell Pepper", title: "Bacterial Spot", desc: "Water-soaked brown spots with yellow chlorotic halos caused by seed-borne Xanthomonas bacteria." },
            { crop: "Bell Pepper", title: "Healthy Foliage", desc: "Glossy deep-green leaves with upright posture and strong flowering nodes." },
            { crop: "Potato", title: "Early Blight", desc: "Concentric target-board rings on lower foliage caused by Alternaria solani; compromises tuber sizing." },
            { crop: "Potato", title: "Late Blight", desc: "Devastating water mold Phytophthora infestans causing oily water-soaked lesions and rapid field collapse." },
            { crop: "Potato", title: "Healthy Foliage", desc: "Lush compound pinnate leaves free of foliar pathogens; supports balanced underground tuberization." },
            { crop: "Tomato", title: "Early Blight", desc: "Progressive defoliation from ground upwards with bullseye lesions; thrives in warm humid weather." },
            { crop: "Tomato", title: "Late Blight", desc: "Aggressive oomycete with white fuzzy spores under leaves during humid mornings; requires urgent isolation." },
            { crop: "Tomato", title: "Healthy Foliage", desc: "Fragrant, deeply serrated dark-green leaflets with active glandular trichomes and zero blemishes." }
        ];

        grid.innerHTML = '';
        catalog.forEach(item => {
            const card = document.createElement('div');
            card.className = 'disease-card';
            card.innerHTML = `
                <div class="disease-card-header">
                    <span class="disease-card-crop">${item.crop}</span>
                    <i class="fa-solid fa-leaf" style="color: var(--emerald-light)"></i>
                </div>
                <h4 class="disease-card-title">${item.title}</h4>
                <p class="disease-card-desc">${item.desc}</p>
            `;
            grid.appendChild(card);
        });
    }

    // Initialize
    loadSamples();
    renderEncyclopedia();
});

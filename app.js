// NeuroDigit Client Engine
document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const canvas = document.getElementById('paintCanvas');
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  const canvasContainer = document.getElementById('canvasContainer');
  const canvasHint = document.getElementById('canvasHint');

  const btnBrush = document.getElementById('btnBrush');
  const btnEraser = document.getElementById('btnEraser');
  const btnUndo = document.getElementById('btnUndo');
  const btnClear = document.getElementById('btnClear');
  const brushSizeInput = document.getElementById('brushSize');
  const strokeSizePreview = document.getElementById('strokeSizePreview');
  const samplePillsContainer = document.getElementById('samplePills');

  // Prediction Display Elements
  const heroDigit = document.getElementById('heroDigit');
  const digitGlow = document.getElementById('digitGlow');
  const heroConfidence = document.getElementById('heroConfidence');
  const heroConfidenceBar = document.getElementById('heroConfidenceBar');
  const confidenceVerdict = document.getElementById('confidenceVerdict');
  const latencyText = document.getElementById('latencyText');

  const tensorCanvas = document.getElementById('tensorCanvas');
  const tensorCtx = tensorCanvas.getContext('2d');
  const tensorPlaceholder = document.getElementById('tensorPlaceholder');

  const altDigit = document.getElementById('altDigit');
  const altConfidence = document.getElementById('altConfidence');
  const entropyValue = document.getElementById('entropyValue');
  const probabilityBars = document.getElementById('probabilityBars');

  // Modal Elements
  const btnToggleInfo = document.getElementById('btnToggleInfo');
  const btnCloseModal = document.getElementById('btnCloseModal');
  const infoModal = document.getElementById('infoModal');
  const metaValAcc = document.getElementById('metaValAcc');
  const historyTableBody = document.getElementById('historyTableBody');

  // State Variables
  let isDrawing = false;
  let activeTool = 'brush'; // 'brush' or 'eraser'
  let brushSize = parseInt(brushSizeInput.value, 10);
  let lastX = 0;
  let lastY = 0;
  let hasStrokes = false;
  const undoStack = [];
  const MAX_UNDO = 15;

  let debounceTimer = null;
  let abortController = null;

  // Initialize Canvas
  function initCanvas() {
    // Fill pure black
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    saveState();
  }

  function saveState() {
    if (undoStack.length >= MAX_UNDO) {
      undoStack.shift();
    }
    undoStack.push(ctx.getImageData(0, 0, canvas.width, canvas.height));
  }

  function undo() {
    if (undoStack.length > 1) {
      undoStack.pop(); // Remove current state
      const prevState = undoStack[undoStack.length - 1];
      ctx.putImageData(prevState, 0, 0);
      checkCanvasEmpty();
      predictDigit();
    } else if (undoStack.length === 1) {
      clearCanvas();
    }
  }

  function clearCanvas() {
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    hasStrokes = false;
    canvasHint.classList.remove('hidden');
    saveState();
    resetPredictionUI();
  }

  function checkCanvasEmpty() {
    const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    let nonBlackPixels = 0;
    for (let i = 0; i < imgData.length; i += 4) {
      if (imgData[i] > 20 || imgData[i + 1] > 20 || imgData[i + 2] > 20) {
        nonBlackPixels++;
      }
    }
    hasStrokes = nonBlackPixels > 30;
    if (hasStrokes) {
      canvasHint.classList.add('hidden');
    } else {
      canvasHint.classList.remove('hidden');
      resetPredictionUI();
    }
    return hasStrokes;
  }

  // Pointer position helpers
  function getPos(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    let clientX = e.clientX;
    let clientY = e.clientY;

    if (e.touches && e.touches.length > 0) {
      clientX = e.touches[0].clientX;
      clientY = e.touches[0].clientY;
    }

    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY
    };
  }

  function startDrawing(e) {
    isDrawing = true;
    canvasContainer.classList.add('drawing');
    const pos = getPos(e);
    lastX = pos.x;
    lastY = pos.y;

    // Draw single dot on click
    draw(e);
  }

  function draw(e) {
    if (!isDrawing) return;
    const pos = getPos(e);

    ctx.beginPath();
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    if (activeTool === 'brush') {
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = brushSize;
    } else {
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = brushSize * 1.5;
    }

    ctx.moveTo(lastX, lastY);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();

    lastX = pos.x;
    lastY = pos.y;

    hasStrokes = true;
    canvasHint.classList.add('hidden');

    // Live prediction with debounce
    triggerDebouncedPredict(70);
  }

  function stopDrawing() {
    if (!isDrawing) return;
    isDrawing = false;
    canvasContainer.classList.remove('drawing');
    saveState();
    checkCanvasEmpty();
    // Immediate prediction upon lifting finger/mouse
    if (hasStrokes) {
      predictDigit();
    }
  }

  // Event Listeners for Canvas
  canvas.addEventListener('mousedown', startDrawing);
  window.addEventListener('mousemove', draw);
  window.addEventListener('mouseup', stopDrawing);

  canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    startDrawing(e);
  }, { passive: false });

  window.addEventListener('touchmove', (e) => {
    if (isDrawing) {
      e.preventDefault();
      draw(e);
    }
  }, { passive: false });

  window.addEventListener('touchend', stopDrawing);
  window.addEventListener('touchcancel', stopDrawing);

  // Tools control
  btnBrush.addEventListener('click', () => {
    activeTool = 'brush';
    btnBrush.classList.add('active');
    btnEraser.classList.remove('active');
  });

  btnEraser.addEventListener('click', () => {
    activeTool = 'eraser';
    btnEraser.classList.add('active');
    btnBrush.classList.remove('active');
  });

  btnUndo.addEventListener('click', undo);
  btnClear.addEventListener('click', clearCanvas);

  brushSizeInput.addEventListener('input', (e) => {
    brushSize = parseInt(e.target.value, 10);
    strokeSizePreview.textContent = `${brushSize}px`;
  });

  // Keyboard Shortcuts
  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'c' || e.key === 'C') {
      clearCanvas();
    } else if (e.key === 'b' || e.key === 'B') {
      btnBrush.click();
    } else if (e.key === 'e' || e.key === 'E') {
      btnEraser.click();
    } else if ((e.ctrlKey || e.metaKey) && (e.key === 'z' || e.key === 'Z')) {
      e.preventDefault();
      undo();
    }
  });

  // Probability Bars Generation
  function initProbabilityBars() {
    probabilityBars.innerHTML = '';
    for (let i = 0; i < 10; i++) {
      const row = document.createElement('div');
      row.className = 'prob-row';
      row.id = `probRow${i}`;
      row.innerHTML = `
        <span class="digit-label">${i}</span>
        <div class="bar-track">
          <div class="bar-fill" id="barFill${i}"></div>
        </div>
        <span class="prob-percentage" id="probPercent${i}">0.0%</span>
      `;
      probabilityBars.appendChild(row);
    }
  }

  function resetPredictionUI() {
    heroDigit.textContent = '?';
    heroDigit.classList.remove('pop');
    digitGlow.style.opacity = '0.3';
    heroConfidence.textContent = '0.0%';
    heroConfidenceBar.style.width = '0%';
    confidenceVerdict.textContent = 'Waiting for stroke...';
    latencyText.textContent = 'Ready';

    tensorPlaceholder.classList.remove('hidden');
    tensorCtx.clearRect(0, 0, tensorCanvas.width, tensorCanvas.height);

    altDigit.textContent = '-';
    altConfidence.textContent = '0%';
    entropyValue.textContent = '-';

    for (let i = 0; i < 10; i++) {
      const row = document.getElementById(`probRow${i}`);
      const fill = document.getElementById(`barFill${i}`);
      const percent = document.getElementById(`probPercent${i}`);
      if (row) row.className = 'prob-row';
      if (fill) fill.style.width = '0%';
      if (percent) percent.textContent = '0.0%';
    }
  }

  function triggerDebouncedPredict(delay) {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      predictDigit();
    }, delay);
  }

  // Real-time Prediction Call
  async function predictDigit() {
    if (!checkCanvasEmpty()) return;

    if (abortController) {
      abortController.abort();
    }
    abortController = new AbortController();

    const dataUrl = canvas.toDataURL('image/png');
    const startTime = performance.now();

    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: dataUrl }),
        signal: abortController.signal
      });

      if (!response.ok) return;

      const data = await response.json();
      const roundTripMs = Math.round(performance.now() - startTime);

      renderPrediction(data, roundTripMs);
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error('Inference error:', err);
      }
    }
  }

  function renderPrediction(data, totalLatency) {
    if (!data || data.prediction === null || data.prediction === undefined) {
      resetPredictionUI();
      return;
    }

    const { prediction, confidence, probabilities, processed_tensor, entropy } = data;

    // Update Hero
    const prevDigit = heroDigit.textContent;
    heroDigit.textContent = prediction;
    if (prevDigit !== String(prediction)) {
      heroDigit.classList.remove('pop');
      void heroDigit.offsetWidth; // trigger reflow
      heroDigit.classList.add('pop');
    }

    heroConfidence.textContent = `${(confidence * 100).toFixed(1)}%`;
    heroConfidenceBar.style.width = `${Math.min(100, confidence * 100)}%`;
    digitGlow.style.opacity = Math.max(0.4, confidence).toString();

    // Confidence verdict styling
    if (confidence > 0.9) {
      confidenceVerdict.textContent = `High certainty recognition`;
      confidenceVerdict.style.color = '#34d399';
    } else if (confidence > 0.6) {
      confidenceVerdict.textContent = `Moderate confidence`;
      confidenceVerdict.style.color = '#38bdf8';
    } else {
      confidenceVerdict.textContent = `Ambiguous pattern`;
      confidenceVerdict.style.color = '#f59e0b';
    }

    // Latency
    latencyText.textContent = `${data.inference_time_ms.toFixed(1)} ms (${totalLatency}ms net)`;

    // Processed Tensor View (28x28)
    if (processed_tensor && processed_tensor.length === 28) {
      tensorPlaceholder.classList.add('hidden');
      drawTensor(processed_tensor);
    }

    // Top 2 and entropy
    const indexedProbs = probabilities.map((p, idx) => ({ digit: idx, prob: p }));
    indexedProbs.sort((a, b) => b.prob - a.prob);

    const top1 = indexedProbs[0];
    const top2 = indexedProbs[1];

    if (top2 && top2.prob > 0.001) {
      altDigit.textContent = top2.digit;
      altConfidence.textContent = `${(top2.prob * 100).toFixed(1)}%`;
    } else {
      altDigit.textContent = '-';
      altConfidence.textContent = '<0.1%';
    }

    if (entropy !== undefined) {
      entropyValue.textContent = entropy.toFixed(3);
    }

    // Update Bars
    for (let i = 0; i < 10; i++) {
      const p = probabilities[i];
      const row = document.getElementById(`probRow${i}`);
      const fill = document.getElementById(`barFill${i}`);
      const percent = document.getElementById(`probPercent${i}`);

      if (!row || !fill || !percent) continue;

      const pPercent = (p * 100).toFixed(1);
      fill.style.width = `${Math.max(1, p * 100)}%`;
      percent.textContent = `${pPercent}%`;

      row.className = 'prob-row';
      if (i === top1.digit) {
        row.classList.add('top-1');
      } else if (top2 && i === top2.digit && top2.prob > 0.05) {
        row.classList.add('top-2');
      }
    }
  }

  // Draw 28x28 normalized tensor matrix to 84x84 canvas
  function drawTensor(matrix28) {
    const scale = tensorCanvas.width / 28;
    for (let r = 0; r < 28; r++) {
      for (let c = 0; c < 28; c++) {
        const val = Math.floor(matrix28[r][c] * 255);
        tensorCtx.fillStyle = `rgb(${val},${val},${val})`;
        tensorCtx.fillRect(c * scale, r * scale, scale, scale);
      }
    }
  }

  // Load sample MNIST benchmark into canvas
  function loadSampleDigit(digitMatrix) {
    // Clear canvas
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Scale 28x28 up to 280x280 smoothly with interpolation
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = 28;
    tempCanvas.height = 28;
    const tempCtx = tempCanvas.getContext('2d');
    const imgData = tempCtx.createImageData(28, 28);

    for (let r = 0; r < 28; r++) {
      for (let c = 0; c < 28; c++) {
        const idx = (r * 28 + c) * 4;
        const val = digitMatrix[r][c];
        imgData.data[idx] = val;
        imgData.data[idx + 1] = val;
        imgData.data[idx + 2] = val;
        imgData.data[idx + 3] = 255;
      }
    }
    tempCtx.putImageData(imgData, 0, 0);

    // Draw scaled up to main canvas with smoothing
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(tempCanvas, 20, 20, canvas.width - 40, canvas.height - 40);

    hasStrokes = true;
    canvasHint.classList.add('hidden');
    saveState();
    predictDigit();
  }

  // Fetch benchmark samples & model metadata
  async function loadMetadata() {
    try {
      const res = await fetch('/api/info');
      if (!res.ok) return;
      const data = await res.json();

      if (data.final_val_accuracy) {
        metaValAcc.textContent = `${data.final_val_accuracy}%`;
      }

      // Populate history table
      if (data.history && data.history.epochs) {
        historyTableBody.innerHTML = '';
        for (let i = 0; i < data.history.epochs.length; i++) {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>Epoch ${data.history.epochs[i]}</td>
            <td>${data.history.train_loss[i]}</td>
            <td>${data.history.train_acc[i]}%</td>
            <td>${data.history.val_loss[i]}</td>
            <td><strong style="color: #34d399">${data.history.val_acc[i]}%</strong></td>
          `;
          historyTableBody.appendChild(row);
        }
      }

      // Populate sample pills (0-9)
      if (data.sample_digits) {
        samplePillsContainer.innerHTML = '';
        for (let d = 0; d < 10; d++) {
          if (data.sample_digits[d]) {
            const btn = document.createElement('button');
            btn.className = 'sample-pill-btn';
            btn.textContent = d;
            btn.title = `Load authentic MNIST sample of digit ${d}`;
            btn.addEventListener('click', () => {
              loadSampleDigit(data.sample_digits[d]);
            });
            samplePillsContainer.appendChild(btn);
          }
        }
      }
    } catch (e) {
      console.warn('Metadata not loaded yet:', e);
    }
  }

  // Modal interactions
  btnToggleInfo.addEventListener('click', () => {
    infoModal.classList.add('open');
  });

  btnCloseModal.addEventListener('click', () => {
    infoModal.classList.remove('open');
  });

  infoModal.addEventListener('click', (e) => {
    if (e.target === infoModal) {
      infoModal.classList.remove('open');
    }
  });

  // Start everything
  initCanvas();
  initProbabilityBars();
  resetPredictionUI();
  loadMetadata();
});

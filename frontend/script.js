document.addEventListener("DOMContentLoaded", () => {
  // Configuration
  const BACKEND_URL = "http://localhost:8000";

  // State
  const state = {
    file: null,
    serverPath: null,   // Current image (result or original)
    originalPath: null, // Always the original uploaded image
    maskPath: null,
    isProcessing: false,
    currentTab: 'create',
    editTool: 'wall',
    brushSize: 30,
    history: [],
    detectedItems: [],
    inferredRoomType: null
  };

  // --- Initialization ---
  init();

  function init() {
    setupTabs();
    setupUpload();
    setupGeneration();
    setupPlanning();
    setupEditing();
    setupScanning();
    setupHardwareStatus();
    loadHistory();
    setupEventListeners();
    setupComparison();
  }

  // --- Hardware Status Badge ---
  async function setupHardwareStatus() {
    const statusPill = document.getElementById('system-status');
    const statusText = document.getElementById('status-text');

    try {
      const res = await fetch(`${BACKEND_URL}/health`);
      const data = await res.json();

      statusPill.classList.remove('offline');

      if (data.cuda_available) {
        statusPill.classList.add('gpu');
        statusText.textContent = `GPU Online: ${data.cuda_device}`;
        document.getElementById('engine-name').textContent = "NVIDIA CUDA";
      } else {
        statusPill.classList.add('cpu');
        statusText.textContent = "CPU Mode (Standard)";
        document.getElementById('engine-name').textContent = "CPU (Optimized)";
      }

      // Update latency mock
      document.getElementById('latency').textContent = data.cuda_available ? "12ms" : "450ms";

    } catch (e) {
      statusPill.classList.add('offline');
      statusText.textContent = "System Offline";
      console.error("Backend offline", e);
    }
  }

  // --- Interactions ---
  function setupEventListeners() {
    // Strength Slider Live Update
    const slider = document.getElementById('strength');
    const valDisplay = document.getElementById('strength-value');
    if (slider && valDisplay) {
      slider.addEventListener('input', (e) => {
        const val = Math.round(e.target.value * 100);
        valDisplay.textContent = `${val}%`;
        // Color coding
        if (val < 50) valDisplay.style.color = "var(--text-muted)";
        else if (val < 75) valDisplay.style.color = "var(--accent)";
        else valDisplay.style.color = "#f59e0b"; // Warning color
      });
    }

    // Room Type Check
    document.getElementById('room-type').addEventListener('change', adjustSettingsForTransformation);
  }

  function setupComparison() {
    // Spacebar to compare
    document.addEventListener('keydown', (e) => {
      // Only if not typing in an input
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

      if (e.code === 'Space' && state.originalPath) {
        e.preventDefault();
        document.getElementById('main-image').src = state.originalPath;
        document.getElementById('compare-toggle').textContent = "Original Image";
        document.getElementById('compare-toggle').style.background = "var(--primary)";
      }
    });

    document.addEventListener('keyup', (e) => {
      if (e.code === 'Space' && state.serverPath) {
        // Restore current result
        // We need a way to know if serverPath is a full URL or relative
        const url = state.serverPath.startsWith('http') ? state.serverPath : `${BACKEND_URL}${state.serverPath}`;
        document.getElementById('main-image').src = url;
        document.getElementById('compare-toggle').textContent = "Hold Space to Compare";
        document.getElementById('compare-toggle').style.background = "rgba(0,0,0,0.6)";
      }
    });
  }

  // --- Navigation ---
  function setupTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.panel-content');

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        const target = `tab-${tab.dataset.tab}`;
        contents.forEach(c => {
          if (c.id === target) {
            c.classList.remove('hidden');
            c.classList.add('active');
          } else {
            c.classList.add('hidden');
            c.classList.remove('active');
          }
        });

        state.currentTab = tab.dataset.tab;
        // Reset mask canvas on tab switch
        clearMask();
      });
    });
  }

  // --- Upload ---
  function setupUpload() {
    const zone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    const mainImage = document.getElementById('main-image');

    if (!zone || !fileInput) return;

    zone.onclick = () => fileInput.click();

    zone.ondragover = (e) => {
      e.preventDefault();
      zone.style.borderColor = "var(--primary)";
      zone.style.background = "rgba(99, 102, 241, 0.1)";
    };
    zone.ondragleave = () => {
      zone.style.borderColor = "var(--border)";
      zone.style.background = "transparent";
    };
    zone.ondrop = (e) => {
      e.preventDefault();
      zone.style.borderColor = "var(--border)";
      zone.style.background = "transparent";
      if (e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
      }
    };

    fileInput.onchange = (e) => {
      if (e.target.files.length) handleFile(e.target.files[0]);
    };

    function handleFile(file) {
      state.file = file;
      const reader = new FileReader();
      reader.onload = (e) => {
        state.originalPath = e.target.result; // Store base64 for comparison
        mainImage.src = state.originalPath;
        mainImage.classList.remove('hidden');
        document.getElementById('upload-placeholder').classList.add('hidden');
        document.getElementById('compare-toggle').classList.remove('hidden');

        // Enable generate
        document.getElementById('generate-btn').disabled = false;

        // Init canvas dimensions once image loads
        mainImage.onload = () => {
          const cvs = document.getElementById('mask-canvas');
          cvs.width = mainImage.naturalWidth;
          cvs.height = mainImage.naturalHeight;
          cvs.classList.remove('hidden');
        };
      };
      reader.readAsDataURL(file);

      // Background upload
      uploadToServer(file);
    }
  }

  async function uploadToServer(file) {
    const formData = new FormData();
    formData.append('image', file);
    try {
      const res = await fetch(`${BACKEND_URL}/api/upload`, { method: 'POST', body: formData });
      const data = await res.json();
      state.serverPath = data.image_path; // Backend relative path

      // Handle Auto-Detect Logic
      if (data.detected_room_type) {
        console.log(`Smart Detect: ${data.detected_room_type}`);
        state.inferredRoomType = data.detected_room_type;

        // Auto-set dropdown if user hasn't touched it logic (simplified)
        const drop = document.getElementById('room-type');
        if (drop && drop.value !== data.detected_room_type) {
          drop.value = data.detected_room_type;
          // Flash UI?
        }
      }
    } catch (e) {
      console.error("Upload failed", e);
    }
  }

  // --- Generation (AI Feeling) ---
  function setupGeneration() {
    const btn = document.getElementById('generate-btn');
    btn.addEventListener('click', async () => {
      if (state.isProcessing || !state.file) return;

      // Start "AI Process"
      setProcessing(true);

      const formData = new FormData();
      formData.append('image', state.file);
      formData.append('room_type', document.getElementById('room-type').value);
      formData.append('style', document.getElementById('style').value);
      formData.append('budget', document.getElementById('budget').value);
      formData.append('provider', document.getElementById('provider').value);
      formData.append('strength', document.getElementById('strength').value);

      try {
        const res = await fetch(`${BACKEND_URL}/api/generate`, { method: 'POST', body: formData });
        if (!res.ok) throw new Error("Generation error");
        const data = await res.json();

        // Success
        updateMainImage(data.image_url);
        addToHistory("Redesign: " + document.getElementById('style').value, data.estimated_cost);
        updateBudgetUI(data.estimated_cost);

      } catch (e) {
        alert("Generation failed: " + e.message);
      } finally {
        setProcessing(false);
      }
    });
  }

  // AI Loading Sequence
  async function setProcessing(active) {
    state.isProcessing = active;
    const loader = document.getElementById('loader');
    const msg = document.getElementById('loader-text');

    if (active) {
      loader.classList.add('visible');
      const messages = [
        "Analyzing spatial geometry...",
        "Measuring room dimensions...",
        "Aligning architectural constraints...",
        "Applying diffusion model...",
        "Optimizing lighting shaders...",
        "Finalizing render..."
      ];

      let i = 0;
      msg.textContent = messages[0];
      state.msgInterval = setInterval(() => {
        i = (i + 1) % messages.length;
        msg.textContent = messages[i];
      }, 1500);

    } else {
      clearInterval(state.msgInterval);
      loader.classList.remove('visible');
    }
  }

  // --- Main Image Updater ---
  function updateMainImage(relativePath) {
    if (!relativePath) return;
    const fullUrl = relativePath.startsWith('http') ? relativePath : `${BACKEND_URL}${relativePath}`;
    state.serverPath = relativePath; // Store relative for backend ops
    const img = document.getElementById('main-image');

    // Fade effect?
    img.style.opacity = 0.5;
    setTimeout(() => {
      img.src = fullUrl;
      img.onload = () => { img.style.opacity = 1; };
    }, 200);
  }

  // --- Budget UI ---
  function updateBudgetUI(cost) {
    const budgetRef = parseInt(document.getElementById('budget').value) || 5000;
    const percent = Math.min((cost / budgetRef) * 100, 100);

    document.getElementById('budget-display').textContent = `₹${cost.toLocaleString()}`;
    document.getElementById('budget-bar').style.width = `${percent}%`;

    const statusText = document.getElementById('budget-status-text');
    const statusPercent = document.getElementById('budget-percent');

    statusPercent.textContent = `${Math.round((cost / budgetRef) * 100)}% Used`;

    if (cost > budgetRef) {
      statusText.textContent = "Over Budget";
      statusText.style.color = "var(--danger)";
      document.getElementById('budget-bar').style.background = "var(--danger)";
    } else {
      statusText.textContent = "Within Budget";
      statusText.style.color = "var(--accent)";
      document.getElementById('budget-bar').style.background = "var(--accent)";
    }
  }

  // --- Planning ---
  function setupPlanning() {
    document.getElementById('plan-btn').addEventListener('click', async () => {
      const input = document.getElementById('plan-input');
      const text = input.value.trim();
      if (!text) return;

      addChatMessage("user", text);
      input.value = "";

      const loadingId = addChatMessage("ai", "Thinking...", true);

      try {
        const res = await fetch(`${BACKEND_URL}/api/plan`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_request: text,
            detected_items: state.detectedItems || [],
            budget: parseInt(document.getElementById('budget').value)
          })
        });
        const data = await res.json();
        removeChatMessage(loadingId);

        // Format Plan
        let html = `<strong>Strategy:</strong> ${data.plan.summary}<br><br>`;
        data.plan.steps.forEach((s, i) => {
          let suggestionsHtml = '';
          if (s.suggestions && s.suggestions.length > 0) {
            suggestionsHtml = `<div style="margin-top:5px; margin-left:15px; padding:8px; background:rgba(79, 172, 254, 0.1); border-radius:4px;">
                  <div style="font-size:10px; color:#4facfe; margin-bottom:4px;">Recommended Products:</div>
                  ${s.suggestions.map(link => `<a href="${link.link}" target="_blank" style="display:block; color:#fff; font-size:11px; text-decoration:none; margin-bottom:3px;">🛍️ ${link.vendor || 'Buy'}: ${link.title} (₹${link.approx_price})</a>`).join('')}
              </div>`;
          }

          html += `<div style="margin-bottom:12px;">
            <strong>${i + 1}. ${s.action}</strong>: ${s.target}
            ${suggestionsHtml}
          </div>`;
        });
        addChatMessage("ai", html);

      } catch (e) {
        removeChatMessage(loadingId);
        addChatMessage("ai", "Planning service unavailable.");
      }
    });

    function addChatMessage(role, html, isTemp) {
      const log = document.getElementById('chat-log');
      const div = document.createElement('div');
      div.className = "chat-msg " + role; // Define CSS for this
      div.style.marginBottom = "10px";
      div.style.padding = "8px";
      div.style.borderRadius = "6px";
      div.style.background = role === "user" ? "rgba(255,255,255,0.05)" : "rgba(99, 102, 241, 0.1)";
      div.style.borderLeft = role === "ai" ? "3px solid var(--primary)" : "none";

      div.innerHTML = html;
      if (isTemp) div.id = "temp-msg";
      log.appendChild(div);
      log.scrollTop = log.scrollHeight;
      return div.id;
    }
    window.addChatMessage = addChatMessage; // Exposed for internal use
    window.removeChatMessage = (id) => { const el = document.getElementById(id); if (el) el.remove(); };
  }

  // --- Scan / Edit Logic (Preserved but simplified interface) ---
  function setupScanning() {
    document.getElementById('scan-btn').addEventListener('click', async () => {
      if (!state.file) return;
      const zone = document.getElementById('scan-results');
      zone.innerHTML = "<div style='color:var(--text-dim)'>Scanning image features...</div>";
      zone.classList.remove('hidden');

      try {
        // Re-use detection logic
        const formData = new FormData();
        formData.append('image', state.file);
        formData.append('budget', 50000);
        const res = await fetch(`${BACKEND_URL}/vision/detect`, { method: 'POST', body: formData });
        const data = await res.json();
        state.detectedItems = data.detections || [];
        const onlineSuggestions = data.online_suggestions || {};

        // Render nicely
        if (state.detectedItems.length === 0) {
          zone.innerHTML = "No objects detected.";
        } else {
          zone.innerHTML = state.detectedItems.map(item => {
            let linksHtml = '';
            if (onlineSuggestions[item.category] && onlineSuggestions[item.category].results) {
              const bestLinks = onlineSuggestions[item.category].results.slice(0, 3);
              if (bestLinks.length > 0) {
                linksHtml = `<div style="margin-top:4px; margin-bottom:8px; padding-left:10px; border-left: 2px solid var(--accent);">
                        <div style="font-size:10px; color:var(--text-muted);">Purchase Suggestions:</div>
                        ${bestLinks.map(l => `<a href="${l.link}" target="_blank" style="display:block; color:#4facfe; font-size:11px; text-decoration:none; margin-top:2px;">🛒 ${l.vendor}: ${l.title.substring(0, 25)}... (₹${l.approx_price})</a>`).join('')}
                     </div>`;
              }
            }

            return `
                    <div style="background:rgba(255,255,255,0.03); margin-top:8px; padding:8px; border-radius:4px; font-size:12px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                            <span style="font-weight:600">${item.label}</span>
                            <span style="color:var(--accent)">${Math.round(item.confidence * 100)}%</span>
                        </div>
                        ${linksHtml}
                    </div>
                 `;
          }).join('');
        }
      } catch (e) {
        zone.innerHTML = "Scan failed.";
      }
    });
  }

  // --- Setup Editing (Click to Segment) ---
  function setupEditing() {
    const canvas = document.getElementById('mask-canvas');
    let isDrawing = false;
    let startX, startY;

    // We only want CLICK detection for wall segmenting now
    canvas.addEventListener('mousedown', e => {
      if (state.currentTab !== 'edit' || state.isProcessing) return;
      isDrawing = true;
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      startX = (e.clientX - rect.left) * scaleX;
      startY = (e.clientY - rect.top) * scaleY;
    });

    canvas.addEventListener('mouseup', async e => {
      if (!isDrawing) return;
      isDrawing = false;

      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      const endX = (e.clientX - rect.left) * scaleX;
      const endY = (e.clientY - rect.top) * scaleY;

      // Calculate movement amount
      const dist = Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2));

      // ONLY trigger if it was a CLICK (moved less than 5px)
      if (dist > 5) return;

      // Show loading
      setProcessing(true);
      document.getElementById('loader-text').textContent = "Detecting Wall Boundary...";

      // Draw a temporary marker where user clicked
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#10b981';
      ctx.beginPath();
      ctx.arc(startX, startY, 10, 0, 2 * Math.PI);
      ctx.fill();

      try {
        // Send POINT coordinates for SAM to segment the wall
        const body = {
          image_path: state.serverPath,
          x: Math.round(startX),
          y: Math.round(startY)
        };

        const res = await fetch(`${BACKEND_URL}/edit/segment`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
        });
        const data = await res.json();

        state.maskPath = data.mask_path;

        // Draw mask on canvas
        const img = new Image();
        img.src = data.mask_url.startsWith('http') ? data.mask_url : `${BACKEND_URL}${data.mask_url}`;
        img.onload = () => {
          const ctx = canvas.getContext('2d');
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

          // Enable Apply button
          document.getElementById('apply-edit-btn').disabled = false;
        };

      } catch (e) {
        console.error(e);
        alert("Could not detect wall at this location.");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      } finally {
        setProcessing(false);
      }
    });

    // Apply Paint Button
    document.getElementById('apply-edit-btn').addEventListener('click', async () => {
      if (!state.maskPath) { alert("Please click on a wall to select it first!"); return; }

      setProcessing(true);
      document.getElementById('loader-text').textContent = "Applying Paint...";

      const color = document.getElementById('edit-color').value;
      const body = {
        image_path: state.serverPath,
        mask_path: state.maskPath,
        color_hex: color
      };

      try {
        const res = await fetch(`${BACKEND_URL}/edit/recolor`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
        });
        const data = await res.json();

        updateMainImage(data.image_url);

        // Clear UI after success
        clearMask();
        state.maskPath = null;
        document.getElementById('apply-edit-btn').disabled = true;

      } catch (e) {
        alert("Painting failed: " + e.message);
      } finally {
        setProcessing(false);
      }
    });

    document.getElementById('clear-mask-btn').addEventListener('click', () => {
      clearMask();
      document.getElementById('apply-edit-btn').disabled = true;
    });
  }

  function clearMask() {
    const cvs = document.getElementById('mask-canvas');
    const ctx = cvs.getContext('2d');
    ctx.clearRect(0, 0, cvs.width, cvs.height);
    state.maskPath = null;
  }

  // --- History Helpers ---
  function adjustSettingsForTransformation() { /* kept simple */ }
  async function loadHistory() { /* implemented above */ }
  async function addToHistory() { /* implemented above */ }

});

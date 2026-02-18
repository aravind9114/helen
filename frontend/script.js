document.addEventListener("DOMContentLoaded", () => {
  // Configuration
  const BACKEND_URL = "http://localhost:8000";

  // State
  const state = {
    file: null,
    serverPath: null,
    maskPath: null,
    isProcessing: false,
    currentTab: 'create',
    editTool: 'wall', // Default to wall paint
    brushSize: 30,
    history: [],
    budgetBreakdown: null
  };

  // DOM Elements - Navigation
  const tabs = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  // DOM Elements - Creation
  const fileInput = document.getElementById('file-input');
  const uploadPlaceholder = document.getElementById('upload-placeholder');
  const mainImage = document.getElementById('main-image');
  const maskCanvas = document.getElementById('mask-canvas');
  const generateBtn = document.getElementById('generate-btn');
  const loader = document.getElementById('loader');
  const loaderText = document.getElementById('loader-text');

  // DOM Elements - Plan
  const planInput = document.getElementById('plan-input');
  const planBtn = document.getElementById('plan-btn');
  const chatLog = document.getElementById('chat-log');
  // Execute Plan button removed

  // DOM Elements - Edit
  const applyEditBtn = document.getElementById('apply-edit-btn');
  const editActionSelect = document.getElementById('edit-action');

  // --- Initialization ---
  init();

  function init() {
    setupTabs();
    setupUpload();
    setupGeneration();
    setupPlanning();
    setupEditing();
    setupScanning();
    loadHistory();
    setupEventListeners(); // Call the new function

    // Listen for room type changes
    document.getElementById('room-type').addEventListener('change', adjustSettingsForTransformation);
  }

  // --- Event Listeners ---
  function setupEventListeners() {
    // Strength Slider Live Update
    const strengthSlider = document.getElementById('strength');
    const strengthValue = document.getElementById('strength-value');
    if (strengthSlider && strengthValue) {
      strengthSlider.addEventListener('input', (e) => {
        const val = Math.round(e.target.value * 100);
        strengthValue.textContent = `${val}%`;

        // Color code
        if (val < 50) strengthValue.style.color = "#888"; // Subtle
        else if (val < 75) strengthValue.style.color = "#4CAF50"; // Balanced
        else strengthValue.style.color = "#FF5722"; // Aggressive
      });
    }
  }

  // --- Navigation ---
  function setupTabs() {
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        // Update active tab button
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Show content
        const targetId = `tab-${tab.dataset.tab}`;
        tabContents.forEach(content => {
          content.classList.toggle('hidden', content.id !== targetId);
          content.classList.toggle('active', content.id === targetId);
        });

        state.currentTab = tab.dataset.tab;

        // Clear masks when switching tabs
        clearMask();
      });
    });
  }

  // --- Upload Handling ---
  function setupUpload() {
    const uploadPlaceholder = document.getElementById('upload-placeholder');
    const fileInput = document.getElementById('file-input'); // Re-select to be safe

    if (!uploadPlaceholder || !fileInput) {
      console.error("Upload elements missing!");
      return;
    }

    // Force click binding
    uploadPlaceholder.onclick = () => {
      console.log("Upload clicked");
      fileInput.click();
    };

    fileInput.addEventListener('change', handleFile);

    // Drag and drop support
    uploadPlaceholder.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadPlaceholder.style.borderColor = 'var(--primary-color)';
    });

    uploadPlaceholder.addEventListener('dragleave', () => {
      uploadPlaceholder.style.borderColor = 'var(--border-color)';
    });

    uploadPlaceholder.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadPlaceholder.style.borderColor = 'var(--border-color)';
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        fileInput.files = files;
        handleFile({ target: fileInput });
      }
    });
  }

  function handleFile(e) {
    const file = e.target.files[0];
    if (!file) return;

    state.file = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      mainImage.src = e.target.result;
      mainImage.classList.remove('hidden');
      uploadPlaceholder.classList.add('hidden');

      // Adjust canvas to match image
      mainImage.onload = () => {
        maskCanvas.width = mainImage.naturalWidth;
        maskCanvas.height = mainImage.naturalHeight;
        maskCanvas.classList.remove('hidden');
      };
    };
    reader.readAsDataURL(file);

    // Upload to server immediately
    uploadToServer(file);
  }

  async function uploadToServer(file) {
    const formData = new FormData();
    formData.append('image', file);
    try {
      const res = await fetch(`${BACKEND_URL}/api/upload`, { method: 'POST', body: formData });
      const data = await res.json();
      state.serverPath = data.image_path;
      console.log("Uploaded to server:", state.serverPath);

      // *** Handle Room Detection ***
      if (data.detected_room_type) {
        console.log(`[Smart Detect] Room: ${data.detected_room_type} (${(data.room_confidence * 100).toFixed(1)}%)`);

        state.inferredRoomType = data.detected_room_type;

        // Show badge
        const badge = document.getElementById('room-detect-badge');
        if (badge) {
          badge.textContent = `Detected: ${data.detected_room_type}`;
          badge.style.display = 'inline-block';
          badge.title = `Confidence: ${(data.room_confidence * 100).toFixed(1)}%`;
        }

        // Auto-select dropdown
        const drop = document.getElementById('room-type');
        if (drop && drop.value !== data.detected_room_type) {
          drop.value = data.detected_room_type;

          // Reset strength since it matches now
          const slider = document.getElementById('strength');
          if (slider) {
            slider.value = 0.55;
            document.getElementById('strength-value').textContent = "55%";
            document.getElementById('strength-value').style.color = "#4CAF50";
          }
        }
      }
    } catch (e) {
      console.error("Upload failed", e);
      alert("Failed to upload image to server.");
    }
  }

  // --- Generation ---
  function setupGeneration() {
    generateBtn.addEventListener('click', async () => {
      if (state.isProcessing || !state.file) return;
      setLoading(true, "Dreaming up your room...");

      const roomType = document.getElementById('room-type').value;
      const style = document.getElementById('style').value;
      const budget = document.getElementById('budget').value;
      const provider = document.getElementById('provider').value;
      // Get strength from slider or default to 0.55
      const strength = document.getElementById('strength') ? document.getElementById('strength').value : "0.55";

      const formData = new FormData();
      formData.append('image', state.file);
      formData.append('room_type', roomType);
      formData.append('style', style);
      formData.append('budget', budget);
      formData.append('provider', provider);
      formData.append('strength', strength);

      console.log(`Generating with strength: ${strength}`);

      try {
        const res = await fetch(`${BACKEND_URL}/api/generate`, { method: 'POST', body: formData });
        if (!res.ok) throw new Error("Generation failed");
        const data = await res.json();

        updateMainImage(data.image_url);
        addToHistory("Generation", data.estimated_cost);

        // Show budget info (Simulated for generation)
        showBudget({
          total_cost: data.estimated_cost,
          breakdown: [{ action: "Redesign", estimated_cost: data.estimated_cost }]
        });

      } catch (e) {
        alert(e.message);
      } finally {
        setLoading(false);
      }
    });
  }

  // --- Planning (LLM) ---
  function setupPlanning() {
    planBtn.addEventListener('click', async () => {
      const request = planInput.value.trim();
      if (!request) return;

      addChatMessage("user", request);
      planInput.value = "";

      // Show thinking
      const thinkingId = addChatMessage("ai", "Thinking...", true);

      try {
        // Ensure we have detected items
        let detectedItems = state.detectedItems || [];

        if (detectedItems.length === 0 && state.file) {
          // Quick auto-detect if not done yet
          try {
            const formData = new FormData();
            formData.append('image', state.file);
            formData.append('budget', 50000); // Dummy budget for detection
            const detRes = await fetch(`${BACKEND_URL}/vision/detect`, { method: 'POST', body: formData });
            const detData = await detRes.json();
            detectedItems = detData.detections || [];
            state.detectedItems = detectedItems; // Cache it
          } catch (e) {
            console.warn("Auto-detection failed, proceeding without context", e);
          }
        }

        const res = await fetch(`${BACKEND_URL}/api/plan`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_request: request,
            detected_items: detectedItems,
            budget: parseInt(document.getElementById('budget').value)
          })
        });

        const data = await res.json();
        removeChatMessage(thinkingId);

        // Plan Display
        if (data.verification && !data.verification.approved) {
          addChatMessage("ai", `⚠️ Budget Warning: ${data.verification.feedback}`);
        }

        let planText = `<strong>Here is my plan:</strong><br>${data.plan.summary}<br><br>`;
        data.plan.steps.forEach((step, i) => {
          planText += `<strong>${i + 1}. ${step.action.toUpperCase()} ${step.target}</strong>: ${step.reason || ""}<br>`;
          // Render suggestions if any
          if (step.suggestions && step.suggestions.length > 0) {
            planText += `<div style="margin-left: 20px; font-size: 0.9em; color: var(--accent);">
                  <em>Suggestions:</em><br>`;
            step.suggestions.forEach(s => {
              planText += `<a href="${s.url}" target="_blank" style="color: #4facfe; text-decoration: underline;">${s.title}</a> (${s.domain}) - ${s.approx_price ? '₹' + s.approx_price : 'Check Price'}<br>`;
            });
            planText += `</div>`;
          }
          planText += `<br>`;
        });

        addChatMessage("ai", planText);
        return; // Explicitly stop execution to prevent ghost errors

        // Execute Plan button removed.
        // planActions.classList.remove('hidden');

      } catch (e) {
        console.error("Plan Error Details:", e);
        removeChatMessage(thinkingId);
        addChatMessage("ai", "Sorry, I encountered an error planning that.");
      }
    });
  }

  // --- Editing (Inpaint/Click) ---
  function setupEditing() {
    // Drag variables
    let isDragging = false;
    let startX, startY;

    // Mouse Down
    maskCanvas.addEventListener('mousedown', (e) => {
      if (state.currentTab !== 'edit' || state.isProcessing) return;
      isDragging = true;
      const rect = maskCanvas.getBoundingClientRect();
      const scaleX = maskCanvas.width / rect.width;
      const scaleY = maskCanvas.height / rect.height;
      startX = (e.clientX - rect.left) * scaleX;
      startY = (e.clientY - rect.top) * scaleY;
    });

    // Mouse Move (Draw Selection Box)
    maskCanvas.addEventListener('mousemove', (e) => {
      if (!isDragging) return;

      const ctx = maskCanvas.getContext('2d');
      // Redraw existing mask image if any (but we might lose it if we clear... 
      // ideally we layer. For now, simple clear to show box).
      // Actually, let's just draw box on top. 
      // We need to redraw the underlying mask if it exists? 
      // Let's assume we are selecting NEW mask so we can clear.

      const rect = maskCanvas.getBoundingClientRect();
      const scaleX = maskCanvas.width / rect.width;
      const scaleY = maskCanvas.height / rect.height;
      const currentX = (e.clientX - rect.left) * scaleX;
      const currentY = (e.clientY - rect.top) * scaleY;

      // Clear and redraw
      // To preserve existing mask, we would need to store it. 
      // For now, let's just clear to show selection clearly.
      ctx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);

      // Repaint main image? No, main image is <img> below canvas.

      ctx.strokeStyle = '#00ff00';
      ctx.lineWidth = 2;
      ctx.strokeRect(startX, startY, currentX - startX, currentY - startY);
    });

    // Mouse Up (Finish Selection)
    maskCanvas.addEventListener('mouseup', async (e) => {
      if (!isDragging) return;
      isDragging = false;

      const rect = maskCanvas.getBoundingClientRect();
      const scaleX = maskCanvas.width / rect.width;
      const scaleY = maskCanvas.height / rect.height;
      const endX = (e.clientX - rect.left) * scaleX;
      const endY = (e.clientY - rect.top) * scaleY;

      const dx = Math.abs(endX - startX);
      const dy = Math.abs(endY - startY);

      let body = { image_path: state.serverPath };

      // Threshold to distinguish click vs drag
      if (dx < 5 && dy < 5) {
        // It's a click
        body.x = Math.round(startX);
        body.y = Math.round(startY);
      } else {
        // It's a box
        // SAM expects [x_min, y_min, x_max, y_max]
        const x_min = Math.round(Math.min(startX, endX));
        const y_min = Math.round(Math.min(startY, endY));
        const x_max = Math.round(Math.max(startX, endX));
        const y_max = Math.round(Math.max(startY, endY));
        body.box = [x_min, y_min, x_max, y_max];
      }

      // Segment
      setLoading(true, "Finding object...");
      try {
        const res = await fetch(`${BACKEND_URL}/edit/segment`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        const data = await res.json();

        state.maskPath = data.mask_path;
        drawMask(data.mask_url);
        applyEditBtn.disabled = false;

      } catch (e) {
        console.error(e);
        alert("Segmentation failed");
      } finally {
        setLoading(false);
      }
    });

    // Apply Edit
    applyEditBtn.addEventListener('click', async () => {
      if (!state.maskPath) return;

      const action = editActionSelect.value;
      setLoading(true, "Applying magic...");

      try {
        let endpoint, body;
        // 'inpaint' = Replace Object
        if (action === 'inpaint' || action === 'remove') {
          endpoint = '/edit/inpaint';
          let prompt = document.getElementById('edit-prompt').value;

          if (action === 'remove') {
            prompt = "empty space, background, wall, floor"; // Force remove prompt
          } else if (!prompt) {
            alert("Please describe what you want to place here.");
            setLoading(false);
            return;
          }

          body = {
            image_path: state.serverPath,
            mask_path: state.maskPath,
            prompt: prompt
          };
        }
        // 'wall' or 'repaint' = Recolor
        else {
          endpoint = '/edit/recolor';
          body = {
            image_path: state.serverPath,
            mask_path: state.maskPath,
            color_hex: document.getElementById('edit-color').value
          };
        }

        const res = await fetch(`${BACKEND_URL}${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });

        const data = await res.json();
        updateMainImage(data.image_url);
        state.maskPath = null;
        clearMask();
        applyEditBtn.disabled = true;

        // Assume generic cost for edit
        addToHistory("Edit: " + action, 500);

      } catch (e) {
        alert(e.message);
      } finally {
        setLoading(false);
      }
    });

    // Toggle input fields
    editActionSelect.addEventListener('change', () => {
      const val = editActionSelect.value;
      document.getElementById('edit-prompt-group').classList.toggle('hidden', val === 'wall' || val === 'remove');
      document.getElementById('edit-color-group').classList.toggle('hidden', val !== 'wall');
    });

    // Initialize UI for Wall Paint
    document.getElementById('edit-prompt-group').classList.add('hidden');
    document.getElementById('edit-color-group').classList.remove('hidden');

    // Tool selection (Single tool now)
    /*
    tools.forEach(btn => {
      btn.addEventListener('click', () => {
        tools.forEach(t => t.classList.remove('active'));
        btn.classList.add('active');
        const tool = btn.dataset.tool;
        state.editTool = tool;

        // Show/Hide inputs based on tool
        document.getElementById('edit-prompt-group').classList.toggle('hidden', tool === 'wall' || tool === 'remove');
        document.getElementById('edit-color-group').classList.toggle('hidden', tool !== 'wall');
      });
    });
    */
  }

  function setupScanning() {
    const scanBtn = document.getElementById('scan-btn');
    if (!scanBtn) return;

    // Click triggers manual detection
    scanBtn.addEventListener('click', () => {
      console.log("Manual Scan Triggered");
      performAutoDetection();
    });

    /* 
    // Removed recursive scanning logic
    */
    // --- Auto-Detection & Smart Logic ---
    async function performAutoDetection() {
      if (!state.file) return;

      console.log("Auto-detecting room context...");
      // Show small loading indicator if possible, or just do it in background

      try {
        const formData = new FormData();
        formData.append('image', state.file);
        formData.append('budget', 50000);

        const res = await fetch(`${BACKEND_URL}/vision/detect`, { method: 'POST', body: formData });
        const data = await res.json();
        state.detectedItems = data.detections || [];

        // Render Results
        const resultsDiv = document.getElementById('scan-results');
        if (resultsDiv) {
          resultsDiv.classList.remove('hidden');
          if (state.detectedItems.length === 0) {
            resultsDiv.innerHTML = "<p>No furniture detected.</p>";
          } else {
            let html = "<div style='display: flex; flex-direction: column; gap: 10px;'>";
            state.detectedItems.forEach(item => {
              html += `
                    <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; border: 1px solid var(--border-color);">
                        <div style="display: flex; justify-content: space-between;">
                            <strong>${item.label || item.category} (${(item.confidence * 100).toFixed(0)}%)</strong>
                        </div>
                    `;

              // Add suggestions links if available
              if (data.online_suggestions && data.online_suggestions[item.category]) {
                const suggestions = data.online_suggestions[item.category].results || [];
                if (suggestions.length > 0) {
                  html += `<div style="margin-top: 5px; font-size: 0.9em;">
                                 <span style="color: #aaa;">🛒 Purchase Links:</span><br>
                             `;
                  suggestions.slice(0, 3).forEach(link => {
                    html += `<a href="${link.link}" target="_blank" style="color: #4facfe; margin-right: 10px; text-decoration: none;">
                                    ${link.title.substring(0, 20)}...
                                 </a>`;
                  });
                  html += `</div>`;
                }
              }
              html += `</div>`;
            });
            html += "</div>";
            resultsDiv.innerHTML = html;
          }
        }

        // Infer Room Type
        const inferredType = inferRoomType(state.detectedItems);
        console.log(`Inferred Room: ${inferredType} `);

        if (inferredType) {
          state.inferredRoomType = inferredType;

          // Auto-Select the dropdown
          const drop = document.getElementById('room-type');
          if (drop && drop.value !== inferredType) {
            // Only auto-set if it's different and user just uploaded
            drop.value = inferredType;
            console.log(`Auto - selected Detected Room: ${inferredType} `);

            // Reset strength to Subtle/Balanced since it matches now
            const slider = document.getElementById('strength');
            if (slider) {
              slider.value = 0.55;
              document.getElementById('strength-value').textContent = "55%";
              document.getElementById('strength-value').style.color = "#4CAF50";
            }
          }
        }

        // Trigger smart adjustment
        adjustSettingsForTransformation();

      } catch (e) {
        console.warn("Auto-detection failed", e);
      }
    }

    function inferRoomType(items) {
      const counts = {};
      items.forEach(i => counts[i.label] = (counts[i.label] || 0) + 1);

      if (counts['bed']) return 'Bedroom';
      if (counts['couch'] || counts['sofa'] || counts['tv monitor']) return 'Living Room';
      if (counts['oven'] || counts['sink'] || counts['refrigerator']) return 'Kitchen';
      if (counts['toilet'] || counts['sink']) return 'Bathroom';
      return null;
    }
  }

  function adjustSettingsForTransformation() {
    const targetType = document.getElementById('room-type').value;
    const detected = state.inferredRoomType;
    const slider = document.getElementById('strength');
    const strengthValue = document.getElementById('strength-value');

    if (!detected || !slider) return;

    // Normalize comparison
    const isMismatch = detected !== targetType; // Simple string match (Dropdown values match inferred strings?)
    // Dropdown values: "Living Room", "Bedroom", "Kitchen".

    if (isMismatch) {
      // Check if it's a structural change (e.g. Bed -> Living)
      if (detected === 'Bedroom' && targetType !== 'Bedroom') {
        console.log("Transformation detected: Bedroom -> Other. Increasing strength.");
        slider.value = 0.85;
        strengthValue.textContent = "85%";
        strengthValue.style.color = "#FF5722";

        // Notify user (Optional toast)
        // alert("Transformation Detected: We increased creativity to 85% to help remove the bed!");
        addChatMessage("ai", "💡 **Tip:** I see a **Bedroom** but you want a **" + targetType + "**. I've boosted creativity to **85%** to help remodel the furniture.");
      } else {
        // Standard mismatch
        slider.value = 0.75;
        strengthValue.textContent = "75%";
      }
    } else {
      // Same room type - Restore balance
      slider.value = 0.55;
      strengthValue.textContent = "55%";
      strengthValue.style.color = "#4CAF50";
    }
  }

  // --- Helpers ---
  function updateMainImage(url) {
    const fullUrl = url.startsWith('http') ? url : `${BACKEND_URL}${url} `;
    state.serverPath = url; // Update current path logic for subsequent edits usually requires keeping track
    // Note: For chaining, we should ideally get the absolute path from backend response.
    // But for display, URL is enough.

    // Re-load image to update canvas dimensions/content
    mainImage.src = fullUrl;

    // IMPORTANT: We need the SERVER PATH for the next edit.
    // The endpoint returns `image_path` (absolute local path) and `image_url`.
    // We need to fetch the response JSON to update state.serverPath properly in the callers.
  }

  function drawMask(url) {
    const ctx = maskCanvas.getContext('2d');
    const img = new Image();
    img.src = url.startsWith('http') ? url : `${BACKEND_URL}${url} `;
    img.onload = () => {
      ctx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);
      ctx.drawImage(img, 0, 0, maskCanvas.width, maskCanvas.height);
    };
  }

  function clearMask() {
    const ctx = maskCanvas.getContext('2d');
    ctx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);
  }

  function setLoading(show, text) {
    state.isProcessing = show;
    loader.classList.toggle('hidden', !show);
    if (text) loaderText.textContent = text;
  }

  function addChatMessage(role, text, isTemp = false) {
    const div = document.createElement('div');
    div.className = `message ${role} `;
    div.innerHTML = text;
    if (isTemp) div.id = "temp-" + Date.now();
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
    return div.id;
  }

  function removeChatMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  // --- History & Budget ---
  async function loadHistory() {
    try {
      const res = await fetch(`${BACKEND_URL}/api/history`);
      const data = await res.json();
      const list = document.getElementById('history-list');

      if (data.length > 0) {
        list.innerHTML = "";
        data.reverse().forEach(item => {
          const div = document.createElement('div');
          div.className = "history-item";
          div.innerHTML = `
              < strong > ${item.project_name || "Session"}</strong >
                <span>$${item.total_cost}</span>
            `;
          list.appendChild(div);
        });
      }
    } catch (e) { console.error(e); }
  }

  async function addToHistory(actionName, cost) {
    try {
      await fetch(`${BACKEND_URL}/api/history`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: "Design " + new Date().toLocaleTimeString(),
          actions: [{ name: actionName }],
          total_cost: cost
        })
      });
      // Refresh history list
      loadHistory();

    } catch (e) { }
  }

  function showBudget(data) {
    if (!data || !data.breakdown) return;

    const panel = document.getElementById('budget-breakdown');
    const details = document.getElementById('cost-details');
    const total = document.getElementById('total-cost');

    panel.classList.remove('hidden');
    details.innerHTML = data.breakdown.map(b =>
      `<div>${b.action} ${b.target || ""}: $${b.estimated_cost}</div>`
    ).join("");
    total.textContent = `$${data.total_cost}`;
  }
});

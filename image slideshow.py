<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✨ Modern Image Slideshow Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --text-primary: white;
            --text-secondary: #cbd5e1;
            --accent: #38bdf8;
            --button-gray: #334155;
            --button-green: #22c55e;
            --button-yellow: #eab308;
            --button-blue: #3b82f6;
            --button-red: #ef4444;
            --status-good: #22c55e;
            --status-warn: #facc15;
            --status-error: red;
            --status-info: #38bdf8;
            --footer-text: #64748b;
        }

        body {
            font-family: 'Helvetica', Arial, sans-serif;
            background-color: var(--bg-primary);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
            transition: all 0.3s ease;
        }

        /* ========= LIGHT THEME ========= */
        body.light-theme {
            --bg-primary: #f8f9fa;
            --bg-secondary: #e9ecef;
            --text-primary: #212529;
            --text-secondary: #495057;
            --accent: #0d6efd;
            --button-gray: #6c757d;
            --button-green: #198754;
            --button-yellow: #ffc107;
            --button-blue: #0d6efd;
            --button-red: #dc3545;
            --status-good: #198754;
            --status-warn: #ff9800;
            --status-error: #dc3545;
            --status-info: #0d6efd;
            --footer-text: #868e96;
        }

        /* ========= PASTEL THEME ========= */
        body.pastel-theme {
            --bg-primary: #faf6f1;
            --bg-secondary: #f5e6d3;
            --text-primary: #5a4a42;
            --text-secondary: #7d6b63;
            --accent: #ff6b9d;
            --button-gray: #c9ada7;
            --button-green: #a8d8da;
            --button-yellow: #fff9a6;
            --button-blue: #ffb4a2;
            --button-red: #e76f51;
            --status-good: #a8d8da;
            --status-warn: #fff9a6;
            --status-error: #e76f51;
            --status-info: #ff6b9d;
            --footer-text: #b5a89b;
        }

        /* ========= FOREST THEME ========= */
        body.forest-theme {
            --bg-primary: #1b4332;
            --bg-secondary: #2d6a4f;
            --text-primary: #d8f3dc;
            --text-secondary: #b7e4c7;
            --accent: #52b788;
            --button-gray: #40916c;
            --button-green: #74c69d;
            --button-yellow: #95d5b2;
            --button-blue: #52b788;
            --button-red: #ff6b6b;
            --status-good: #74c69d;
            --status-warn: #95d5b2;
            --status-error: #ff6b6b;
            --status-info: #52b788;
            --footer-text: #81b29a;
        }

        .container {
            width: 100%;
            max-width: 1300px;
        }

        .theme-toggle-container {
            position: fixed;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            z-index: 1000;
            flex-wrap: wrap;
            justify-content: flex-end;
        }

        .theme-btn {
            padding: 8px 12px;
            border: 2px solid var(--text-primary);
            background-color: var(--bg-secondary);
            color: var(--text-primary);
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            transition: all 0.3s ease;
        }

        .theme-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }

        .theme-btn.active {
            background-color: var(--accent);
            color: var(--bg-primary);
            border-color: var(--accent);
        }

        .header {
            text-align: center;
            color: var(--text-primary);
            font-size: 30px;
            font-weight: bold;
            margin-bottom: 30px;
            margin-top: 80px;
        }

        .image-frame {
            background-color: var(--bg-secondary);
            border-radius: 8px;
            padding: 25px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }

        .image-label {
            max-width: 900px;
            max-height: 650px;
            object-fit: contain;
            border-radius: 4px;
        }

        .image-name-label {
            text-align: center;
            font-size: 14px;
            font-weight: bold;
            color: var(--accent);
            margin-bottom: 10px;
        }

        .speed-control-section {
            text-align: center;
            margin-bottom: 25px;
        }

        .speed-label {
            font-size: 13px;
            color: var(--text-primary);
            margin-bottom: 10px;
            display: block;
        }

        .speed-slider {
            width: 350px;
            height: 6px;
            border-radius: 3px;
            background: var(--button-gray);
            outline: none;
            -webkit-appearance: none;
            appearance: none;
        }

        .speed-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: var(--button-green);
            cursor: pointer;
        }

        .speed-slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: var(--button-green);
            cursor: pointer;
            border: none;
        }

        .controls {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }

        button {
            font-size: 14px;
            font-weight: bold;
            padding: 12px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            color: var(--text-primary);
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }

        button:active {
            transform: translateY(0);
        }

        .prev-btn {
            background-color: var(--button-gray);
        }

        .play-btn {
            background-color: var(--button-green);
        }

        .pause-btn {
            background-color: var(--button-yellow);
            color: var(--bg-primary);
        }

        .next-btn {
            background-color: var(--button-gray);
        }

        .add-btn {
            background-color: var(--button-blue);
        }

        .remove-btn {
            background-color: var(--button-red);
        }

        .image-counter {
            text-align: center;
            font-size: 15px;
            color: var(--text-secondary);
            margin-bottom: 10px;
        }

        .status-label {
            text-align: center;
            font-size: 13px;
            color: var(--status-info);
            margin-bottom: 20px;
            min-height: 20px;
        }

        .footer {
            text-align: center;
            font-size: 11px;
            color: var(--footer-text);
            padding-top: 20px;
            border-top: 1px solid var(--button-gray);
        }

        .file-input-wrapper {
            display: none;
        }

        @media (max-width: 768px) {
            .header {
                font-size: 24px;
                margin-bottom: 20px;
                margin-top: 140px;
            }

            .image-frame {
                padding: 15px;
                margin-bottom: 15px;
            }

            .controls {
                gap: 5px;
            }

            button {
                padding: 10px 15px;
                font-size: 12px;
            }

            .speed-slider {
                width: 80%;
                max-width: 300px;
            }

            .theme-toggle-container {
                flex-direction: column;
                top: 10px;
                right: 10px;
                gap: 5px;
            }

            .theme-btn {
                padding: 6px 10px;
                font-size: 11px;
            }
        }
    </style>
</head>
<body>
    <div class="theme-toggle-container">
        <button class="theme-btn active" onclick="switchTheme('dark')">🌙 Dark</button>
        <button class="theme-btn" onclick="switchTheme('light')">☀️ Light</button>
        <button class="theme-btn" onclick="switchTheme('pastel')">🌸 Pastel</button>
        <button class="theme-btn" onclick="switchTheme('forest')">🌲 Forest</button>
    </div>

    <div class="container">
        <div class="header">📸 Interactive Slideshow Viewer</div>

        <div class="image-frame">
            <img id="imageLabel" class="image-label" src="" alt="Slideshow Image">
        </div>

        <div class="image-name-label" id="imageNameLabel">🖼 Welcome</div>

        <div class="speed-control-section">
            <label class="speed-label">⏱ Slideshow Speed</label>
            <input type="range" id="speedSlider" class="speed-slider" min="1000" max="10000" value="3000">
        </div>

        <div class="controls">
            <button class="prev-btn" onclick="previousImage()">⏮ Previous</button>
            <button class="play-btn" onclick="startSlideshow()">▶ Play</button>
            <button class="pause-btn" onclick="stopSlideshow()">⏸ Pause</button>
            <button class="next-btn" onclick="nextImage()">⏭ Next</button>
            <button class="add-btn" onclick="addImages()">➕ Add Images</button>
            <button class="remove-btn" onclick="removeCurrentImage()">🗑 Remove</button>
        </div>

        <div class="image-counter" id="imageCounter">Image 1 / 1</div>
        <div class="status-label" id="statusLabel">✨ Ready</div>

        <div class="footer">Built with HTML + CSS + JavaScript 💙</div>
    </div>

    <input type="file" id="fileInput" class="file-input-wrapper" multiple accept="image/*">

    <script>
        // =========================================
        // THEME MANAGEMENT
        // =========================================
        function switchTheme(theme) {
            document.body.className = '';
            if (theme === 'light') {
                document.body.classList.add('light-theme');
            } else if (theme === 'pastel') {
                document.body.classList.add('pastel-theme');
            } else if (theme === 'forest') {
                document.body.classList.add('forest-theme');
            }
            
            // Update active button
            document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Save theme to localStorage
            localStorage.setItem('selectedTheme', theme);
        }

        // Load saved theme on page load
        window.addEventListener('load', function() {
            const savedTheme = localStorage.getItem('selectedTheme') || 'dark';
            const themeButtons = document.querySelectorAll('.theme-btn');
            themeButtons.forEach(btn => {
                if (btn.textContent.includes(savedTheme === 'dark' ? '🌙' : 
                    savedTheme === 'light' ? '☀️' : 
                    savedTheme === 'pastel' ? '🌸' : '🌲')) {
                    btn.classList.add('active');
                }
            });
            
            if (savedTheme !== 'dark') {
                document.body.classList.add(savedTheme + '-theme');
            }
        });

        // =========================================
        // VARIABLES
        // =========================================
        let imagePaths = [];
        let currentIndex = 0;
        let running = false;
        let speed = 3000;
        let slideshowTimeout = null;

        // =========================================
        // LOAD SAMPLE IMAGES
        // =========================================
        function initializeSampleImages() {
            // Using sample images from Unsplash (public URLs)
            imagePaths = [
                'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=900&h=650&fit=crop',
                'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=900&h=650&fit=crop',
                'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=900&h=650&fit=crop'
            ];
            showImage(0);
        }

        // =========================================
        // SHOW IMAGE FUNCTION
        // =========================================
        function showImage(index) {
            if (imagePaths.length === 0) {
                document.getElementById('imageLabel').src = '';
                document.getElementById('imageNameLabel').textContent = '🖼 No images loaded';
                return;
            }

            currentIndex = index % imagePaths.length;
            const imagePath = imagePaths[currentIndex];

            document.getElementById('imageLabel').src = imagePath;

            document.getElementById('imageCounter').textContent =
                `Image ${currentIndex + 1} / ${imagePaths.length}`;

            // Extract filename from URL or use generic name
            const imageName = imagePath.split('/').pop().split('?')[0] || `Image ${currentIndex + 1}`;
            document.getElementById('imageNameLabel').textContent = `🖼 ${imageName}`;
        }

        // =========================================
        // AUTO SLIDESHOW
        // =========================================
        function autoSlide() {
            if (running) {
                nextImage();
                slideshowTimeout = setTimeout(autoSlide, speed);
            }
        }

        // =========================================
        // BUTTON FUNCTIONS
        // =========================================
        function startSlideshow() {
            if (!running && imagePaths.length > 0) {
                running = true;
                autoSlide();
                const statusLabel = document.getElementById('statusLabel');
                statusLabel.textContent = '▶ Slideshow Running';
                statusLabel.style.color = 'var(--status-good)';
            }
        }

        function stopSlideshow() {
            running = false;
            clearTimeout(slideshowTimeout);
            const statusLabel = document.getElementById('statusLabel');
            statusLabel.textContent = '⏸ Slideshow Paused';
            statusLabel.style.color = 'var(--status-warn)';
        }

        function nextImage() {
            currentIndex++;
            showImage(currentIndex);
        }

        function previousImage() {
            currentIndex--;
            showImage(currentIndex);
        }

        // =========================================
        // KEYBOARD CONTROLS
        // =========================================
        document.addEventListener('keydown', function(event) {
            if (event.key === 'ArrowRight') {
                nextImage();
            } else if (event.key === 'ArrowLeft') {
                previousImage();
            } else if (event.key === ' ') {
                event.preventDefault();
                if (running) {
                    stopSlideshow();
                } else {
                    startSlideshow();
                }
            }
        });

        // =========================================
        // ADD IMAGES
        // =========================================
        function addImages() {
            document.getElementById('fileInput').click();
        }

        document.getElementById('fileInput').addEventListener('change', function(event) {
            const files = event.target.files;
            if (files.length > 0) {
                for (let file of files) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        imagePaths.push(e.target.result);
                    };
                    reader.readAsDataURL(file);
                }
                setTimeout(() => {
                    showImage(currentIndex);
                    const statusLabel = document.getElementById('statusLabel');
                    statusLabel.textContent = '✅ New Images Added';
                    statusLabel.style.color = 'var(--status-good)';
                }, 500);
            }
        });

        // =========================================
        // REMOVE CURRENT IMAGE
        // =========================================
        function removeCurrentImage() {
            if (imagePaths.length <= 1) {
                const statusLabel = document.getElementById('statusLabel');
                statusLabel.textContent = '❌ Cannot remove last image';
                statusLabel.style.color = 'var(--status-error)';
                return;
            }

            imagePaths.splice(currentIndex, 1);
            currentIndex = 0;
            showImage(currentIndex);

            const statusLabel = document.getElementById('statusLabel');
            statusLabel.textContent = '🗑 Image Removed';
            statusLabel.style.color = 'var(--status-error)';
        }

        // =========================================
        // SPEED CONTROL
        // =========================================
        document.getElementById('speedSlider').addEventListener('input', function(event) {
            speed = parseInt(event.target.value);
        });

        // =========================================
        // INITIALIZE
        // =========================================
        window.addEventListener('load', initializeSampleImages);
    </script>
</body>
</html>

/* ===================================================================
   MAHI SOLAR — CINEMATIC 3D SOLAR PANEL & SUNLIGHT ASSEMBLY SCENE
   Powered by Three.js & GSAP ScrollTrigger
   =================================================================== */

(function () {
  'use strict';

  let scene, camera, renderer;
  let solarGridGroup;
  const solarCells = [];
  let sunMesh, sunGlowMesh, sunLight;
  let lightRaysGroup, particleSystem;
  let energyPulseMesh;

  const mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
  let scrollProgress = 0;

  document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('webgl-canvas-container');
    const canvas = document.getElementById('webgl-canvas');
    if (!container || !canvas || typeof THREE === 'undefined') {
      console.warn("Mahi Solar 3D: Canvas or Three.js library not available.");
      return;
    }

    init3DScene(canvas);
    createSunAndBeams();
    createSolarPanelGrid();
    createStarfieldParticles();
    createEnergyPulse();
    bindEvents();
    setupGSAPScrollIntegration();
    animate();
  });

  function init3DScene(canvas) {
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x050811, 0.010);

    camera = new THREE.PerspectiveCamera(
      45,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.set(0, 0, 18);

    renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      alpha: true,
      antialias: true,
      powerPreference: "high-performance"
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.6;

    // Lighting setup
    const ambientLight = new THREE.AmbientLight(0x2a3b5c, 2.0);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffe599, 3.5);
    dirLight.position.set(5, 12, 10);
    scene.add(dirLight);

    sunLight = new THREE.PointLight(0xffb300, 6, 60);
    sunLight.position.set(0, 6, -1);
    scene.add(sunLight);
  }

  /* -------------------------------------------------------------------
     1. CREATE GLOWING SUN & RADIANT LIGHT RAYS
     ------------------------------------------------------------------- */
  function createSunAndBeams() {
    const sunGroup = new THREE.Group();
    sunGroup.position.set(0, 7.5, -4);

    // Inner Core Sun Sphere
    const sunGeo = new THREE.SphereGeometry(1.4, 32, 32);
    const sunMat = new THREE.MeshBasicMaterial({
      color: 0xffcc33,
    });
    sunMesh = new THREE.Mesh(sunGeo, sunMat);
    sunGroup.add(sunMesh);

    // Outer Glowing Corona
    const glowGeo = new THREE.SphereGeometry(2.2, 32, 32);
    const glowMat = new THREE.MeshBasicMaterial({
      color: 0xff8c00,
      transparent: true,
      opacity: 0.35,
      side: THREE.BackSide
    });
    sunGlowMesh = new THREE.Mesh(glowGeo, glowMat);
    sunGroup.add(sunGlowMesh);

    // Light Ray Cylinder Beams descending from Sun
    lightRaysGroup = new THREE.Group();
    const rayCount = 12;
    for (let i = 0; i < rayCount; i++) {
      const rayGeo = new THREE.CylinderGeometry(0.02, 0.4 + Math.random() * 0.3, 12, 8, 1, true);
      const rayMat = new THREE.MeshBasicMaterial({
        color: 0xffd700,
        transparent: true,
        opacity: 0.15 + Math.random() * 0.15,
        side: THREE.DoubleSide,
        blending: THREE.AdditiveBlending
      });
      const ray = new THREE.Mesh(rayGeo, rayMat);
      const angle = (i / rayCount) * Math.PI * 2;
      const radius = 0.5 + Math.random() * 1.5;
      ray.position.set(Math.cos(angle) * radius, -6, Math.sin(angle) * radius);
      ray.rotation.z = (Math.random() - 0.5) * 0.3;
      ray.rotation.x = (Math.random() - 0.5) * 0.3;
      lightRaysGroup.add(ray);
    }
    sunGroup.add(lightRaysGroup);
    scene.add(sunGroup);
  }

  /* -------------------------------------------------------------------
     2. CREATE EXPLODED 3D SOLAR PANEL CELL GRID
     ------------------------------------------------------------------- */
  function createSolarPanelGrid() {
    solarGridGroup = new THREE.Group();
    solarGridGroup.position.set(0, -0.5, 0);

    const cols = 6;
    const rows = 4;
    const cellW = 1.3;
    const cellH = 1.3;
    const cellGap = 0.08;

    const totalW = cols * (cellW + cellGap);
    const totalH = rows * (cellH + cellGap);

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const cellGroup = new THREE.Group();

        // 1. Photovoltaic Silicon Wafer
        const waferGeo = new THREE.BoxGeometry(cellW, cellH, 0.12);
        const waferMat = new THREE.MeshStandardMaterial({
          color: 0x0f4c81,
          roughness: 0.15,
          metalness: 0.85,
          emissive: 0x004488,
          emissiveIntensity: 0.4
        });
        const wafer = new THREE.Mesh(waferGeo, waferMat);
        cellGroup.add(wafer);

        // 2. Silver/Gold Busbar Conductors
        const busGeo = new THREE.BoxGeometry(cellW * 0.95, 0.02, 0.09);
        const busMat = new THREE.MeshStandardMaterial({
          color: 0xd4af37,
          metalness: 0.9,
          roughness: 0.1
        });
        const busbar1 = new THREE.Mesh(busGeo, busMat);
        busbar1.position.y = cellH * 0.25;
        const busbar2 = new THREE.Mesh(busGeo, busMat);
        busbar2.position.y = -cellH * 0.25;
        cellGroup.add(busbar1);
        cellGroup.add(busbar2);

        // 3. Metallic Outer Frame
        const frameGeo = new THREE.BoxGeometry(cellW + 0.04, cellH + 0.04, 0.04);
        const frameMat = new THREE.MeshStandardMaterial({
          color: 0x222a36,
          metalness: 0.9,
          roughness: 0.3
        });
        const frame = new THREE.Mesh(frameGeo, frameMat);
        frame.position.z = -0.03;
        cellGroup.add(frame);

        // Target Assembled Position
        const targetX = (c * (cellW + cellGap)) - (totalW / 2) + cellW / 2;
        const targetY = (r * (cellH + cellGap)) - (totalH / 2) + cellH / 2;
        const targetZ = 0;

        // Scattered (Broken/Exploded) Fragment Position & Rotations
        const randAngle = Math.random() * Math.PI * 2;
        const randDist = 4 + Math.random() * 8;
        const brokenX = targetX + Math.cos(randAngle) * randDist;
        const brokenY = targetY + Math.sin(randAngle) * randDist + (Math.random() - 0.5) * 4;
        const brokenZ = (Math.random() - 0.5) * 12 + 4;

        const brokenRotX = (Math.random() - 0.5) * Math.PI * 3;
        const brokenRotY = (Math.random() - 0.5) * Math.PI * 3;
        const brokenRotZ = (Math.random() - 0.5) * Math.PI * 2;

        cellGroup.position.set(brokenX, brokenY, brokenZ);
        cellGroup.rotation.set(brokenRotX, brokenRotY, brokenRotZ);

        // Store references for scroll lerping
        solarCells.push({
          mesh: cellGroup,
          waferMat: waferMat,
          targetPos: new THREE.Vector3(targetX, targetY, targetZ),
          targetRot: new THREE.Euler(0, 0, 0),
          brokenPos: new THREE.Vector3(brokenX, brokenY, brokenZ),
          brokenRot: new THREE.Euler(brokenRotX, brokenRotY, brokenRotZ)
        });

        solarGridGroup.add(cellGroup);
      }
    }

    // Initial inclination tilt
    solarGridGroup.rotation.x = 0.4;
    scene.add(solarGridGroup);
  }

  /* -------------------------------------------------------------------
     3. FLOATING AMBIENT PARTICLES (STARDUST & PHOTONS)
     ------------------------------------------------------------------- */
  function createStarfieldParticles() {
    const particleCount = 600;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const goldColor = new THREE.Color(0xffb300);
    const cyanColor = new THREE.Color(0x00e5ff);

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 35;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 35;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 30;

      const mixedColor = Math.random() > 0.4 ? goldColor : cyanColor;
      colors[i * 3] = mixedColor.r;
      colors[i * 3 + 1] = mixedColor.g;
      colors[i * 3 + 2] = mixedColor.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.12,
      vertexColors: true,
      transparent: true,
      opacity: 0.7,
      blending: THREE.AdditiveBlending
    });

    particleSystem = new THREE.Points(geometry, material);
    scene.add(particleSystem);
  }

  /* -------------------------------------------------------------------
     4. ENERGY WAVE PULSE RING
     ------------------------------------------------------------------- */
  function createEnergyPulse() {
    const ringGeo = new THREE.RingGeometry(0.1, 4.5, 64);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0xffcc00,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0,
      blending: THREE.AdditiveBlending
    });
    energyPulseMesh = new THREE.Mesh(ringGeo, ringMat);
    energyPulseMesh.rotation.x = Math.PI / 2;
    energyPulseMesh.position.set(0, -0.5, 0);
    scene.add(energyPulseMesh);
  }

  /* -------------------------------------------------------------------
     5. BIND MOUSE & RESIZE EVENTS
     ------------------------------------------------------------------- */
  function bindEvents() {
    window.addEventListener('mousemove', (e) => {
      mouse.targetX = (e.clientX / window.innerWidth - 0.5) * 2;
      mouse.targetY = (e.clientY / window.innerHeight - 0.5) * 2;
    });

    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  }

  /* -------------------------------------------------------------------
     6. GSAP SCROLLTRIGGER INTEGRATION
     ------------------------------------------------------------------- */
  function setupGSAPScrollIntegration() {
    gsap.registerPlugin(ScrollTrigger);

    ScrollTrigger.create({
      trigger: "body",
      start: "top top",
      end: "bottom bottom",
      scrub: 1.2,
      onUpdate: (self) => {
        scrollProgress = self.progress;
      }
    });
  }

  /* -------------------------------------------------------------------
     7. ANIMATION LOOP & SCROLL RENDER LOGIC
     ------------------------------------------------------------------- */
  function animate(timestamp) {
    requestAnimationFrame(animate);

    // Smooth mouse parallax interpolation
    mouse.x += (mouse.targetX - mouse.x) * 0.05;
    mouse.y += (mouse.targetY - mouse.y) * 0.05;

    camera.position.x = mouse.x * 1.5;
    camera.position.y = -mouse.y * 1.2;
    camera.lookAt(0, 0, 0);

    const time = timestamp * 0.001 || 0;

    // Pulse Sun & Rays
    if (sunGlowMesh) {
      sunGlowMesh.scale.setScalar(1 + Math.sin(time * 2) * 0.06);
    }
    if (lightRaysGroup) {
      lightRaysGroup.rotation.y = time * 0.15;
    }
    if (particleSystem) {
      particleSystem.rotation.y = time * 0.03;
    }

    // Scroll Progress Phased Animation
    // Phase 1: 0.0 to 0.35 -> Solar Panel Fragments assemble & snap into place
    const assembleProgress = Math.min(Math.max(scrollProgress / 0.35, 0), 1);
    const easeAssembly = gsap.parseEase("power3.inOut")(assembleProgress);

    solarCells.forEach(cell => {
      cell.mesh.position.lerpVectors(cell.brokenPos, cell.targetPos, easeAssembly);

      cell.mesh.rotation.x = THREE.MathUtils.lerp(cell.brokenRot.x, cell.targetRot.x, easeAssembly);
      cell.mesh.rotation.y = THREE.MathUtils.lerp(cell.brokenRot.y, cell.targetRot.y, easeAssembly);
      cell.mesh.rotation.z = THREE.MathUtils.lerp(cell.brokenRot.z, cell.targetRot.z, easeAssembly);
    });

    // Phase 2: 0.30 to 0.65 -> Sunlight absorption & Cell Energizing
    const chargeProgress = Math.min(Math.max((scrollProgress - 0.30) / 0.35, 0), 1);
    solarCells.forEach(cell => {
      if (chargeProgress > 0) {
        cell.waferMat.emissive.setHex(0xffb300);
        cell.waferMat.emissiveIntensity = chargeProgress * 0.85 + Math.sin(time * 5) * 0.15;
      } else {
        cell.waferMat.emissive.setHex(0x003366);
        cell.waferMat.emissiveIntensity = 0.2;
      }
    });

    // Phase 3: 0.65 to 0.88 -> Array 3D Tilt & Energy Shockwave Wave
    if (scrollProgress >= 0.65 && scrollProgress < 0.88) {
      const tiltProg = (scrollProgress - 0.65) / 0.23;
      solarGridGroup.rotation.x = THREE.MathUtils.lerp(0.4, -0.6, tiltProg);
      solarGridGroup.rotation.y = THREE.MathUtils.lerp(0, 0.4, tiltProg);

      if (energyPulseMesh) {
        energyPulseMesh.material.opacity = (1 - tiltProg) * 0.6;
        energyPulseMesh.scale.setScalar(1 + tiltProg * 3);
      }
    } else {
      if (solarGridGroup && scrollProgress < 0.65) {
        solarGridGroup.rotation.x = THREE.MathUtils.lerp(0.4, 0.2, scrollProgress / 0.65);
        solarGridGroup.rotation.y = 0;
      }
      if (energyPulseMesh) energyPulseMesh.material.opacity = 0;
    }

    // Phase 4: 0.88 to 1.0 -> Zoom into Hero Section
    if (scrollProgress >= 0.88) {
      const zoomProg = (scrollProgress - 0.88) / 0.12;
      camera.position.z = THREE.MathUtils.lerp(18, 4, zoomProg);
      if (solarGridGroup) {
        solarGridGroup.position.z = THREE.MathUtils.lerp(0, -6, zoomProg);
      }
    } else {
      camera.position.z = 18;
      if (solarGridGroup) solarGridGroup.position.z = 0;
    }

    renderer.render(scene, camera);
  }

})();

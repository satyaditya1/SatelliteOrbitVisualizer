# plots/earth_3d.py
import plotly.graph_objects as go
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from .colors import BG, TEXT, PRIMARY_ACCENT
import json

def build_3d_earth_orbit(xs, ys, zs, sat_name="satellite", animate=False, frame_count=100, premium=True):
    """
    Build 3D Earth orbit visualization.
    
    Args:
        xs, ys, zs: Orbit coordinates
        sat_name: Satellite name
        animate: Animation flag (for future use)
        frame_count: Animation frames
        premium: Use premium Three.js Earth with NASA textures if True
    
    Returns:
        Plotly figure or Three.js HTML component (if premium)
    """
    
    if premium:
        return build_premium_earth_visualization(xs, ys, zs, sat_name)
    else:
        return build_plotly_earth_orbit(xs, ys, zs, sat_name)

def build_plotly_earth_orbit(xs, ys, zs, sat_name="satellite"):
    """Legacy Plotly-based Earth visualization."""
    # Earth mesh
    radius = 6371.0
    theta = np.linspace(0, 2*np.pi, 80)
    phi = np.linspace(0, np.pi, 40)
    th, ph = np.meshgrid(theta, phi)
    X = radius * np.cos(th) * np.sin(ph)
    Y = radius * np.sin(th) * np.sin(ph)
    Z = radius * np.cos(ph)

    fig = go.Figure()

    fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Blues',
                             showscale=False, opacity=0.9, hoverinfo='skip', name='Earth'))

    # orbit line
    fig.add_trace(go.Scatter3d(x=xs, y=ys, z=zs, mode='lines', name=sat_name,
                                line=dict(color=PRIMARY_ACCENT, width=2)))

    # starting marker
    fig.add_trace(go.Scatter3d(x=[xs[0]], y=[ys[0]], z=[zs[0]], mode='markers+text',
                              marker=dict(size=4, color=PRIMARY_ACCENT), text=[sat_name],
                              textposition='top center', showlegend=False))

    fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
                                aspectmode='data'),
                      paper_bgcolor=BG, plot_bgcolor=BG, font=dict(color=TEXT),
                      margin=dict(l=0, r=0, t=30, b=0))
    return fig

def build_premium_earth_visualization(xs, ys, zs, sat_name="satellite"):
    """
    Premium Earth with realistic textures from Three.js examples (CDN-hosted).
    Uses WebGL for photorealistic rendering with atmosphere and lighting.
    """
    
    # Convert orbit data to JSON - scale down from km to viewing units
    xs_scaled = [x / 1000.0 for x in xs]
    ys_scaled = [y / 1000.0 for y in ys]
    zs_scaled = [z / 1000.0 for z in zs]
    
    xs_json = json.dumps(xs_scaled)
    ys_json = json.dumps(ys_scaled)
    zs_json = json.dumps(zs_scaled)
    
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Premium Earth Orbit Visualizer</title>
        <style>
            body {{ margin: 0; overflow: hidden; background: #000000; font-family: Arial, sans-serif; }}
            canvas {{ display: block; width: 100%; height: 100%; }}
            #info {{ 
                position: absolute; top: 20px; left: 20px; color: #fff; 
                font-family: monospace; font-size: 13px; background: rgba(0, 0, 0, 0.85);
                padding: 15px 20px; border-radius: 8px; z-index: 10; border: 1px solid #4db8ff;
            }}
            #coordinates {{
                position: absolute; top: 20px; right: 20px; color: #fff;
                font-family: monospace; font-size: 12px; background: rgba(0, 0, 0, 0.85);
                padding: 15px 20px; border-radius: 8px; z-index: 10; border: 1px solid #ff6b6b;
            }}
            #info div {{ margin: 5px 0; }}
            .label {{ color: #888; }}
            .value {{ color: #4db8ff; font-weight: bold; }}
            .coord-label {{ color: #ff6b6b; }}
            .coord-value {{ color: #00ff00; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div id="info">
            <div><strong style="color: #fff; font-size: 14px;">{sat_name}</strong></div>
            <div><span class="label">Orbit Points:</span> <span class="value" id="pointCount">0</span></div>
            <div style="margin-top: 10px; border-top: 1px solid #333; padding-top: 10px; font-size: 12px; color: #aaa;">
                <div>🖱️  Drag to rotate</div>
                <div>🔍 Scroll to zoom</div>
            </div>
        </div>
        <div id="coordinates">
            <div style="color: #ff6b6b; font-weight: bold; margin-bottom: 8px;">SAT COORDINATES</div>
            <div><span class="coord-label">X:</span> <span class="coord-value" id="coordX">0.000</span> km</div>
            <div><span class="coord-label">Y:</span> <span class="coord-value" id="coordY">0.000</span> km</div>
            <div><span class="coord-label">Z:</span> <span class="coord-value" id="coordZ">0.000</span> km</div>
            <div style="margin-top: 8px; border-top: 1px solid #333; padding-top: 8px;">
                <div><span class="coord-label">Alt:</span> <span class="coord-value" id="altitude">0.000</span> km</div>
            </div>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
            // ===== SETUP =====
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x000000);
            
            // ===== ADD STARFIELD =====
            const starGeometry = new THREE.BufferGeometry();
            const starCount = 2000;
            const starPositions = new Float32Array(starCount * 3);
            
            for (let i = 0; i < starCount * 3; i += 3) {{
                starPositions[i] = (Math.random() - 0.5) * 500;     // X
                starPositions[i + 1] = (Math.random() - 0.5) * 500; // Y
                starPositions[i + 2] = (Math.random() - 0.5) * 500; // Z
            }}
            
            starGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
            const starMaterial = new THREE.PointsMaterial({{
                color: 0xffffff,
                size: 0.3,
                sizeAttenuation: true
            }});
            const stars = new THREE.Points(starGeometry, starMaterial);
            scene.add(stars);
            
            const camera = new THREE.PerspectiveCamera(
                75, 
                window.innerWidth / window.innerHeight, 
                0.1, 
                100000
            );
            camera.position.set(0, 8, 12);
            camera.lookAt(0, 0, 0);
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.outputColorSpace = THREE.SRGBColorSpace;
            document.body.appendChild(renderer.domElement);

            // ===== RESPONSIVE =====
            window.addEventListener('resize', () => {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }});

            // ===== MOUSE DRAG =====
            let isDragging = false;
            let previousMouse = {{ x: 0, y: 0 }};
            let cameraRotation = {{ x: 0, y: 0 }};
            
            document.addEventListener('mousedown', (e) => {{ isDragging = true; }});
            document.addEventListener('mousemove', (e) => {{
                if (isDragging) {{
                    const deltaX = e.clientX - previousMouse.x;
                    const deltaY = e.clientY - previousMouse.y;
                    cameraRotation.y += deltaX * 0.008;
                    cameraRotation.x += deltaY * 0.008;
                }}
                previousMouse = {{ x: e.clientX, y: e.clientY }};
            }});
            document.addEventListener('mouseup', () => {{ isDragging = false; }});

            // ===== ZOOM =====
            document.addEventListener('wheel', (e) => {{
                e.preventDefault();
                const currentDist = camera.position.length();
                const newDist = Math.max(5, Math.min(200, currentDist + e.deltaY * 0.05));
                const direction = camera.position.clone().normalize();
                camera.position.copy(direction.multiplyScalar(newDist));
            }}, {{ passive: false }});

            // ===== LOAD TEXTURES FROM CDN =====
            const loader = new THREE.TextureLoader();
            let texturesLoaded = 0;
            
            const earthDayUrl = "https://cdn.jsdelivr.net/gh/mrdoob/three.js/examples/textures/planets/earth_atmos_2048.jpg";
            const earthNightUrl = "https://cdn.jsdelivr.net/gh/mrdoob/three.js/examples/textures/planets/earth_night_2048.png";
            
            let earthDayTex = null;
            let earthNightTex = null;
            
            console.log('Loading textures from CDN...');
            
            // Load day map
            loader.load(
                earthDayUrl,
                (texture) => {{
                    earthDayTex = texture;
                    texture.generateMipmaps = true;
                    texture.magFilter = THREE.LinearFilter;
                    texture.minFilter = THREE.LinearMipmapLinearFilter;
                    texturesLoaded++;
                    console.log('Day texture loaded');
                    updateEarthMaterial();
                }},
                undefined,
                (err) => {{
                    console.error('Failed to load day texture:', err);
                }}
            );
            
            // Load night map
            loader.load(
                earthNightUrl,
                (texture) => {{
                    earthNightTex = texture;
                    texture.generateMipmaps = true;
                    texture.magFilter = THREE.LinearFilter;
                    texture.minFilter = THREE.LinearMipmapLinearFilter;
                    texturesLoaded++;
                    console.log('Night texture loaded');
                    updateEarthMaterial();
                }},
                undefined,
                (err) => {{
                    console.error('Failed to load night texture:', err);
                }}
            );

            // ===== CREATE EARTH =====
            const earthGeo = new THREE.SphereGeometry(6.371, 256, 256);
            const earthMat = new THREE.MeshPhongMaterial({{
                color: 0xffffff,
                shininess: 15,
                wireframe: false
            }});
            const earth = new THREE.Mesh(earthGeo, earthMat);
            earth.rotation.z = THREE.MathUtils.degToRad(23.4);
            scene.add(earth);
            
            // Update material once textures load
            function updateEarthMaterial() {{
                if (earthDayTex) {{
                    earth.material.map = earthDayTex;
                    earth.material.needsUpdate = true;
                }}
                if (earthNightTex) {{
                    earth.material.emissiveMap = earthNightTex;
                    earth.material.emissive = new THREE.Color(0x111111);
                    earth.material.emissiveIntensity = 0.5;
                    earth.material.needsUpdate = true;
                }}
            }}

            // ===== CREATE CLOUDS =====
            const cloudGeo = new THREE.SphereGeometry(6.39, 128, 128);
            const cloudMat = new THREE.MeshPhongMaterial({{
                color: 0xffffff,
                transparent: true,
                opacity: 0.15,
                depthWrite: false,
                emissive: new THREE.Color(0x999999)
            }});
            const clouds = new THREE.Mesh(cloudGeo, cloudMat);
            clouds.rotation.z = earth.rotation.z;
            scene.add(clouds);

            // ===== CREATE ATMOSPHERE =====
            const atmGeo = new THREE.SphereGeometry(6.50, 64, 64);
            const atmMat = new THREE.ShaderMaterial({{
                uniforms: {{}},
                vertexShader: `
                    varying vec3 vNormal;
                    void main() {{
                        vNormal = normalize(normalMatrix * normal);
                        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                    }}
                `,
                fragmentShader: `
                    varying vec3 vNormal;
                    void main() {{
                        float intensity = pow(0.6 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 4.0);
                        gl_FragColor = vec4(0.2, 0.6, 1.0, 0.3) * intensity;
                    }}
                `,
                blending: THREE.AdditiveBlending,
                side: THREE.BackSide,
                transparent: true,
                depthWrite: false
            }});
            const atmosphere = new THREE.Mesh(atmGeo, atmMat);
            scene.add(atmosphere);

            // ===== LIGHTING =====
            const sunLight = new THREE.DirectionalLight(0xffffff, 1.5);
            sunLight.position.set(100, 50, 80);
            scene.add(sunLight);

            const ambLight = new THREE.AmbientLight(0x505050);
            scene.add(ambLight);

            // ===== ORBIT DATA =====
            const orbitXs = {xs_json};
            const orbitYs = {ys_json};
            const orbitZs = {zs_json};
            
            document.getElementById('pointCount').textContent = orbitXs.length;

            // ===== CREATE ORBIT LINE =====
            const orbitPoints = [];
            for (let i = 0; i < orbitXs.length; i++) {{
                orbitPoints.push(new THREE.Vector3(orbitXs[i], orbitYs[i], orbitZs[i]));
            }}

            const orbitGeo = new THREE.BufferGeometry().setFromPoints(orbitPoints);
            const orbitMat = new THREE.LineBasicMaterial({{ 
                color: 0x4db8ff,
                linewidth: 2,
                transparent: false
            }});
            const orbitLine = new THREE.Line(orbitGeo, orbitMat);
            scene.add(orbitLine);

            // ===== CREATE REALISTIC SATELLITE MODEL =====
            const satelliteGroup = new THREE.Group();
            
            // Main body (rectangular box)
            const bodyGeo = new THREE.BoxGeometry(0.4, 0.3, 0.25);
            const bodyMat = new THREE.MeshPhongMaterial({{ 
                color: 0xcccccc,
                shininess: 80,
                metalness: 0.8
            }});
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            satelliteGroup.add(body);
            
            // Solar panels (two large flat rectangles)
            const panelGeo = new THREE.PlaneGeometry(0.6, 0.2);
            const panelMat = new THREE.MeshPhongMaterial({{ 
                color: 0x1a4d99,
                side: THREE.DoubleSide,
                shininess: 40,
                emissive: 0x001a33
            }});
            
            const leftPanel = new THREE.Mesh(panelGeo, panelMat);
            leftPanel.position.set(-0.35, 0.15, 0);
            leftPanel.rotation.y = Math.PI / 6;
            satelliteGroup.add(leftPanel);
            
            const rightPanel = new THREE.Mesh(panelGeo, panelMat);
            rightPanel.position.set(0.35, 0.15, 0);
            rightPanel.rotation.y = -Math.PI / 6;
            satelliteGroup.add(rightPanel);
            
            // Antenna (thin cylinder)
            const antennaGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.3);
            const antennaMat = new THREE.MeshPhongMaterial({{ color: 0x888888 }});
            const antenna = new THREE.Mesh(antennaGeo, antennaMat);
            antenna.position.set(0, 0.25, 0);
            satelliteGroup.add(antenna);
            
            // Dish antenna (small cone)
            const dishGeo = new THREE.ConeGeometry(0.08, 0.12, 16);
            const dishMat = new THREE.MeshPhongMaterial({{ color: 0xffaa00 }});
            const dish = new THREE.Mesh(dishGeo, dishMat);
            dish.position.set(0, -0.2, 0);
            dish.rotation.z = Math.PI;
            satelliteGroup.add(dish);
            
            scene.add(satelliteGroup);

            // Position satellite at first point
            if (orbitPoints.length > 0) {{
                satelliteGroup.position.copy(orbitPoints[0]);
            }}

            // ===== ANIMATION =====
            let pointIndex = 0;
            let frameCounter = 0;
            const movementSpeed = 10; // Move every N frames (slower movement)
            
            function animate() {{
                requestAnimationFrame(animate);

                // Update camera rotation
                const distance = camera.position.length();
                
                if (!isDragging) {{
                    cameraRotation.y += 0.0003;
                }}
                
                const radius = Math.sqrt(camera.position.x * camera.position.x + camera.position.z * camera.position.z);
                camera.position.x = radius * Math.sin(cameraRotation.y);
                camera.position.z = radius * Math.cos(cameraRotation.y);
                camera.position.y = distance * Math.sin(cameraRotation.x);
                
                camera.lookAt(0, 0, 0);

                // Auto-rotate Earth
                earth.rotation.y += 0.0002;
                clouds.rotation.y += 0.00025;

                // Animate satellite along orbit (slowed down)
                if (orbitPoints.length > 0) {{
                    frameCounter++;
                    if (frameCounter >= movementSpeed) {{
                        frameCounter = 0;
                        pointIndex = (pointIndex + 1) % orbitPoints.length;
                        satelliteGroup.position.copy(orbitPoints[pointIndex]);
                        
                        // Point satellite toward Earth (at origin)
                        const earthDir = new THREE.Vector3(0, 0, 0).sub(satelliteGroup.position).normalize();
                        satelliteGroup.lookAt(satelliteGroup.position.clone().add(earthDir));
                        
                        // Update coordinates display
                        const satX = satelliteGroup.position.x * 1000; // Convert back to km
                        const satY = satelliteGroup.position.y * 1000;
                        const satZ = satelliteGroup.position.z * 1000;
                        const altitude = satelliteGroup.position.length() * 1000 - 6371; // Altitude above Earth surface
                        
                        document.getElementById('coordX').textContent = satX.toFixed(3);
                        document.getElementById('coordY').textContent = satY.toFixed(3);
                        document.getElementById('coordZ').textContent = satZ.toFixed(3);
                        document.getElementById('altitude').textContent = altitude.toFixed(3);
                    }}
                }}

                renderer.render(scene, camera);
            }}

            animate();
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=800)

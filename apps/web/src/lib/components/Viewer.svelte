<svelte:options runes={true} />

<script lang="ts">
	import { onMount } from 'svelte';

	let canvasEl: HTMLCanvasElement;

	let resizeObserver: ResizeObserver | null = null;
	let disposeScene: (() => void) | null = null;

	onMount(() => {
		(async () => {
			const THREE = await import('three');
			const { OrbitControls } = await import('three/examples/jsm/controls/OrbitControls.js');
			const { GLTFLoader } = await import('three/examples/jsm/loaders/GLTFLoader.js');

			const renderer = new THREE.WebGLRenderer({ canvas: canvasEl, antialias: true });
			renderer.setPixelRatio(window.devicePixelRatio);
			renderer.setClearColor(0x20232a);

			const scene = new THREE.Scene();

			const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
			camera.position.set(2.5, 2.5, 2.5);

			const controls = new OrbitControls(camera, renderer.domElement);
			controls.enableDamping = true;

			const light = new THREE.DirectionalLight(0xffffff, 1.2);
			light.position.set(5, 10, 7.5);
			scene.add(light);

			const ambient = new THREE.AmbientLight(0xffffff, 0.4);
			scene.add(ambient);

			const loader = new GLTFLoader();
			loader.load(
				'/models/box.glb',
				(gltf: any) => {
					scene.add(gltf.scene);

					const box = new THREE.Box3().setFromObject(gltf.scene);
					const size = box.getSize(new THREE.Vector3()).length();
					const center = box.getCenter(new THREE.Vector3());

					controls.reset();
					controls.target.copy(center);
					camera.position.copy(center);
					camera.position.x += size * 1.5;
					camera.position.y += size * 1.0;
					camera.position.z += size * 1.5;
					camera.lookAt(center);
					controls.update();
				},
				undefined,
				(error: unknown) => {
					// eslint-disable-next-line no-console
					console.error('Failed to load GLB', error);
				}
			);

			const resize = () => {
				const { clientWidth, clientHeight } = canvasEl;
				if (clientWidth === 0 || clientHeight === 0) return;
				renderer.setSize(clientWidth, clientHeight, false);
				camera.aspect = clientWidth / clientHeight;
				camera.updateProjectionMatrix();
			};

			resize();
			resizeObserver = new ResizeObserver(resize);
			resizeObserver.observe(canvasEl);

			let frameId: number;
			const animate = () => {
				frameId = requestAnimationFrame(animate);
				controls.update();
				renderer.render(scene, camera);
			};
			animate();

			disposeScene = () => {
				cancelAnimationFrame(frameId);
				resizeObserver?.disconnect();
				controls.dispose();
				renderer.dispose();

				scene.traverse((obj: any) => {
					if (!obj.isMesh) return;
					if (obj.geometry) {
						obj.geometry.dispose();
					}
					if (obj.material) {
						const materials = Array.isArray(obj.material) ? obj.material : [obj.material];
						for (const m of materials) {
							if (m.map) m.map.dispose();
							if (m.lightMap) m.lightMap.dispose();
							if (m.aoMap) m.aoMap.dispose();
							if (m.emissiveMap) m.emissiveMap.dispose();
							if (m.bumpMap) m.bumpMap.dispose();
							if (m.normalMap) m.normalMap.dispose();
							if (m.specularMap) m.specularMap.dispose();
							if (m.envMap) m.envMap.dispose();
							m.dispose();
						}
					}
				});
			};
		})();

		return () => {
			disposeScene?.();
		};
	});
</script>

<div class="viewer-root">
	<canvas bind:this={canvasEl} class="viewer-canvas"></canvas>
</div>

<style>
	.viewer-root {
		width: 100%;
		height: 100%;
		display: flex;
	}

	.viewer-canvas {
		width: 100%;
		height: 100%;
		display: block;
	}
</style>


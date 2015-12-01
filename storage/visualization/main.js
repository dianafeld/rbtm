if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

var stats;

var camera, controls, scene, renderer, uniforms;

init();
animate();

function init() {


	// variables from "numbers.js" : NMK, R_arr, G_arr, B_arr, A_arr, X_arr, Y_arr, Z_arr
	var N = NMK[0];
	var M = NMK[1];
	var K = NMK[2];


	var medianPointSize =  1;

			


	scene = new THREE.Scene();

	renderer = new THREE.WebGLRenderer();
	renderer.setPixelRatio( window.devicePixelRatio );
	renderer.setSize( window.innerWidth, window.innerHeight );

	var container = document.getElementById( 'container' );
	container.appendChild( renderer.domElement );


	var CMW = 1.1, wDivH = window.innerWidth / window.innerHeight;
	//camera = new THREE.OrthographicCamera( - maxAbsX * CMW * wDivH, maxAbsX * CMW * wDivH, maxAbsY * CMW, - maxAbsY * CMW, 0.1, 1000 );
	camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 1, 1000 );

	camera.position.z = 500;

	controls = new THREE.TrackballControls( camera, renderer.domElement );
	//controls.addEventListener( 'change', render ); // add this only if there is no animation loop (requestAnimationFrame)
	controls.enableDamping = true;
	controls.dampingFactor = 0.25;
	controls.enableZoom = false;



	var	geometry = new THREE.BufferGeometry();


	var colors = new Float32Array( numVertices * 3 );
	var alphas = new Float32Array( numVertices * 1 );
	var positions = new Float32Array( numVertices * 3 );


	for (var i = 0; i < numVertices; i++){
		colors[i * 3] =  (R_arr[i] / 512);
		colors[i * 3 + 1] =  (G_arr[i] / 512);
		colors[i * 3 + 2] =  (B_arr[i] / 512);
		alphas[i] = (A_arr[i] / 512);
		positions[i * 3] =  X_arr[i];
		positions[i * 3 + 1] =  Y_arr[i];
		positions[i * 3 + 2] =  Z_arr[i];
	}

   	geometry.addAttribute( 'color', new THREE.BufferAttribute( colors, 3 ) );
   	geometry.addAttribute( 'alpha', new THREE.BufferAttribute( alphas, 1 ) );
   	geometry.addAttribute( 'position', new THREE.BufferAttribute( positions, 3 ) );



	var shaderMaterial = new THREE.RawShaderMaterial( {

		uniforms: { 
			time: { type: "f", value: 1.0 },
			median_pSize:  { type: "f", value: medianPointSize },
		},
		vertexShader: document.getElementById( 'vertexshader' ).textContent,
		fragmentShader: document.getElementById( 'fragmentshader' ).textContent,
		transparent: true

	} );

	var particleSystem = new THREE.Points( geometry ,shaderMaterial);
	scene.add(particleSystem);


	//  add  FPS stats in upper left corner, can delete it
	stats = new Stats();
	stats.domElement.style.position = 'absolute';
	stats.domElement.style.top = '0px';
	stats.domElement.style.zIndex = 100;
	container.appendChild( stats.domElement );


	window.addEventListener( 'resize', onWindowResize, false );
	alert("Draw!");

}

function onWindowResize() {

	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();

	renderer.setSize( window.innerWidth, window.innerHeight );

}

function animate() {

	requestAnimationFrame( animate );

	controls.update(); // required if controls.enableDamping = true, or if controls.autoRotate = true

	stats.update();

	render();

}

function render() {

	renderer.render( scene, camera );
	renderer.setClearColor( 0xcccccc, 1);

}
if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

var stats;

var camera, controls, scene, renderer, uniforms;

init();
animate();

function init() {

	// variables from "numbers.js" : NMK, maxAbsX, maxAbsY, maxAbsZ, numVertices and numbers
	var N = NMK[0];
	var M = NMK[1];
	var K = NMK[2];

	var medianPointSize = (Math.min (2 * maxAbsX / N, 2 * maxAbsY / M, 2 * maxAbsZ / K)) * 10; //5

			


	scene = new THREE.Scene();

	renderer = new THREE.WebGLRenderer();
	renderer.setPixelRatio( window.devicePixelRatio );
	renderer.setSize( window.innerWidth, window.innerHeight );

	var container = document.getElementById( 'container' );
	container.appendChild( renderer.domElement );


	var CMW = 1.1, wDivH = window.innerWidth / window.innerHeight;
	//camera = new THREE.OrthographicCamera( - maxAbsX * CMW * wDivH, maxAbsX * CMW * wDivH, maxAbsY * CMW, - maxAbsY * CMW, 0.1, 1000 );
	camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 1, 1000 );

	camera.position.z = 50;

	controls = new THREE.TrackballControls( camera, renderer.domElement );
	//controls.addEventListener( 'change', render ); // add this only if there is no animation loop (requestAnimationFrame)
	controls.enableDamping = true;
	controls.dampingFactor = 0.25;
	controls.enableZoom = false;



	var	geometry = new THREE.BufferGeometry();


	if (numbers === []){
		// This is case when max and min values in reconstruction are the same - very rare case, appearing 
		// primarily when you test with couple of points

		numVertices = N * M * K;
		function convertToX(binNum){	return (2 * binNum/N - 1.0) * maxAbsX;	}
		function convertToY(binNum){	return (2 * binNum/M - 1.0) * maxAbsY;	}
		function convertToZ(binNum){	return (2 * binNum/K - 1.0) * maxAbsZ;	}

		var ind = 0;
		var positions = new Float32Array( M * N * K * 3 );
		for (var i = 0; i < N; i++){
			for (var j = 0; j < M; j++){
				for (var k = 0; k < K; k++){
					positions[ind * 3]     = convertToX(i);
					positions[ind * 3 + 1] = convertToY(j);
					positions[ind * 3 + 2] = convertToZ(k);
					ind++;
				}
			}
		}

    	var colors = new Float32Array( numVertices * 3 );
    	var alphas = new Float32Array( numVertices * 1 );
    	for (var i = 0; i < numVertices; i++){
    		colors[i * 3] = 0;
    		colors[i * 3 + 1] = 1;
    		colors[i * 3 + 2] = 0;
    		alphas[i] = 0.5;
    	}
	} else {
		// This is normal case

	    var colors = new Float32Array( numVertices * 3 );
	    var alphas = new Float32Array( numVertices * 1 );
		var positions = new Float32Array( numVertices * 3 );


		var ind = 0;
					

		for (var i = 0; i < numbers.length - 1; i++){
			colors[ind * 3] =  numbers[i++];
			colors[ind * 3 + 1] =  numbers[i++];
			colors[ind * 3 + 2] =  numbers[i++];
			alphas[ind] = numbers[i++];
			positions[ind * 3] =  numbers[i++];
			positions[ind * 3 + 1] =  numbers[i++];
			positions[ind * 3 + 2] =  numbers[i];
			ind++;
		}
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
if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

var stats;

var camera, controls, scene, renderer, uniforms, camera2, renderer2, controls2, plane, cam2_lookAt;
var particleSystems, minThreshold, maxThreshold;

var sliderElement = document.getElementById('slider');
var sliderXElement = document.getElementById('sliderX');
var sliderYElement = document.getElementById('sliderY');
var sliderZElement = document.getElementById('sliderZ');
var sliderMinElement = document.getElementById('sliderMin');
var sliderMaxElement = document.getElementById('sliderMax');


init();
animate();


sliderMinElement.min = 0;
sliderMinElement.max = group_count;
sliderMinElement.step = 1;
sliderMaxElement.min = 0;
sliderMaxElement.max = group_count;
sliderMaxElement.step = 1;

sliderMinElement.addEventListener('input', function () {
	minThreshold = sliderMinElement.value;
	var for_alert = "";
	for (var i_g = 0; i_g < group_count; i_g++){
		particleSystems[i_g].visible = (minThreshold <= i_g && i_g < maxThreshold);
		for_alert += i_g + ": " + particleSystems[i_g].visible + "\n";
	}
	//alert(for_alert);
}, false);

sliderMaxElement.addEventListener('input', function () {
	maxThreshold = sliderMaxElement.value;
	var for_alert = "";
	for (var i_g = 0; i_g < group_count; i_g++){
		particleSystems[i_g].visible = (minThreshold <= i_g && i_g < maxThreshold);
		for_alert += i_g + ": " + particleSystems[i_g].visible + "\n";
	}
	//alert(for_alert);
}, false);


function init() {


	// variables from "numbers.js" : NMK, R_arr, G_arr, B_arr, A_arr, X_arr, Y_arr, Z_arr
	var N = NMK[0];
	var M = NMK[1];
	var K = NMK[2];


	var medianPointSize =  1;




	scene = new THREE.Scene();


	var container = document.getElementById( 'container' );

	renderer = new THREE.WebGLRenderer();
	renderer.setPixelRatio( window.devicePixelRatio ); //need to change, we don't look at window size anymore
	renderer.setSize( container.clientWidth, container.clientHeight );
	renderer.sortObjects = false;

	container.appendChild( renderer.domElement );

	camera = new THREE.PerspectiveCamera( 75, container.clientWidth / container.clientHeight, 0.1, 1000 );

	camera.position.z = 500;


	controls = new THREE.TrackballControls( camera, renderer.domElement );
	//controls.addEventListener( 'change', render ); // add this only if there is no animation loop (requestAnimationFrame)
	controls.enableDamping = true;
	controls.dampingFactor = 0.25;
	controls.enableZoom = false;

/*

	var for_plane = document.getElementById( 'for_plane' );

	renderer2 = new THREE.WebGLRenderer();
	//renderer2.setPixelRatio( window.devicePixelRatio );
	renderer2.setSize( for_plane.clientWidth,  for_plane.clientHeight );
	renderer2.domElement.style.position = 'absolute';
	for_plane.appendChild( renderer2.domElement );


	camera2 = new THREE.OrthographicCamera( -400, 400, -400, 400, 1, 2 );
	cam2_lookAt = new THREE.Vector3(500, 500, 500);
	camera2.lookAt(cam2_lookAt);
	//camera2.position.z = 0;
	//controls2 = new THREE.TrackballControls( camera2, renderer2.domElement );
	//controls2.target.set(300, 300, 300);

*/
	
	particleSystems = [];
	for (var g_i = 0; g_i < group_count; g_i++){

		var	geometry = new THREE.BufferGeometry();

		var positions_int = points[g_i];
		//alert(g_i + ": " + positions_int);
		var positions = new Float32Array( positions_int.length * 3 );	
		for (var i = 0; i < positions_int.length; i++){
			positions[i] =  positions_int[i];
		}
   		geometry.addAttribute( 'position', new THREE.BufferAttribute( positions, 3 ) );

   		var rgba = RGBA[g_i];
		var groupColor = new THREE.Color(rgba[0], rgba[1], rgba[2]);
		var pointsMaterial = new THREE.PointsMaterial({color:groupColor, size: rgba[3]*1.4});
		var particleSystem = new THREE.Points( geometry ,pointsMaterial);

		particleSystems.push(particleSystem);
		scene.add(particleSystem);

	}



/*	var my_plane_geom = new THREE.PlaneGeometry( 800, 800);
	my_plane_geom.position = camera2.position;
	my_plane_geom.quaternion = camera2.quaternion;
	var my_plane_mat = new THREE.MeshBasicMaterial( {color: 0x000000, side: THREE.DoubleSide,
													opacity: 0.3, transparent: true} );
	plane = new THREE.Mesh( my_plane_geom, my_plane_mat );
	scene.add( plane );
	scene.add( camera2 );


	addGrid(400, 100);
	addNumbers(400, 100);
*/


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
	//need to change, also we don't look at window size anymore
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();

	renderer.setSize( window.innerWidth, window.innerHeight );

}

function animate() {

	requestAnimationFrame( animate );

	//controls.update(); // required if controls.enableDamping = true, or if controls.autoRotate = true
	//controls2.update(); // required if controls.enableDamping = true, or if controls.autoRotate = true
	controls.update();
	stats.update();

	//bind_plane_with_cam2();
	render();
	//render2();

}

function render() {
	renderer.render( scene, camera );
	renderer.setClearColor( 0xeeeeee, 1);
}

function render2() {
	renderer2.render( scene, camera2 );
	renderer2.setClearColor( 0xffffff, 1);
}
function bind_plane_with_cam2()
{
	plane.position.copy(camera2.position);
	plane.quaternion.copy(camera2.quaternion);
}


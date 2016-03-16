if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

var stats;

var camera, controls, scene, renderer, uniforms, camera2, renderer2, controls2, plane, cam2_lookAt;
var particleSystems, minThreshold = group_count * 0.75, maxThreshold = group_count;

var sliderElement = document.getElementById('slider');
var sliderXElement = document.getElementById('sliderX');
var sliderYElement = document.getElementById('sliderY');
var sliderZElement = document.getElementById('sliderZ');
var sliderMinElement = document.getElementById('sliderMin');
var sliderMaxElement = document.getElementById('sliderMax');

sliderMinElement.max = group_count;
sliderMaxElement.max = group_count;
sliderMinElement.defaultValue = minThreshold;
sliderMaxElement.defaultValue = maxThreshold;

/*
$("for_plane").click(function(event){
      alert("Поздравляем! Вы починили код!");
   });
*/

function sign(x) { return x < 0 ? -1 : 1; }

sliderElement.addEventListener('input', function () {
	var distance = sliderElement.value;
	var n = new THREE.Vector3();
	n.copy(cam2_lookAt);
	n.normalize();

	var coef = sign(n.x) * sign(n.y) * sign(n.z);
	n.multiplyScalar(  coef *  distance );
	camera2.position.copy(n);
	document.getElementById('slider_out').innerHTML = sliderElement.value;
}, false);

sliderXElement.addEventListener('input', function () {
	cam2_lookAt.x = sliderXElement.value * 500;
	camera2.lookAt(cam2_lookAt);
}, false);
sliderYElement.addEventListener('input', function () {
	cam2_lookAt.y = sliderYElement.value * 500;
	camera2.lookAt(cam2_lookAt);
}, false);
sliderZElement.addEventListener('input', function () {
	cam2_lookAt.z = sliderZElement.value * 500;
	camera2.lookAt(cam2_lookAt);
}, false);

function makeTextSprite( message, parameters )
{
    if ( parameters === undefined ) parameters = {};
    var fontface = parameters.hasOwnProperty("fontface") ? parameters["fontface"] : "Arial";
    var fontsize = parameters.hasOwnProperty("fontsize") ? parameters["fontsize"] : 70;
    var borderThickness = parameters.hasOwnProperty("borderThickness") ? parameters["borderThickness"] : 4;
    var borderColor = parameters.hasOwnProperty("borderColor") ?parameters["borderColor"] : { r:0, g:0, b:0, a:1.0 };
    var backgroundColor = parameters.hasOwnProperty("backgroundColor") ?parameters["backgroundColor"] : { r:255, g:255, b:255, a:1.0 };
    var textColor = parameters.hasOwnProperty("textColor") ?parameters["textColor"] : { r:0, g:0, b:0, a:1.0 };

    var canvas = document.createElement('canvas');
    var context = canvas.getContext('2d');
    context.font = "Bold " + fontsize + "px " + fontface;
    var metrics = context.measureText( message );
    var textWidth = metrics.width;

    context.fillStyle   = "rgba(" + backgroundColor.r + "," + backgroundColor.g + "," + backgroundColor.b + "," + backgroundColor.a + ")";
    context.strokeStyle = "rgba(" + borderColor.r + "," + borderColor.g + "," + borderColor.b + "," + borderColor.a + ")";

    context.lineWidth = borderThickness;

    context.fillStyle = "rgba("+textColor.r+", "+textColor.g+", "+textColor.b+", 1.0)";
    context.fillText( message, borderThickness, fontsize + borderThickness);

    var texture = new THREE.Texture(canvas); 
    texture.needsUpdate = true;

    var spriteMaterial = new THREE.SpriteMaterial( { map: texture, useScreenCoordinates: false } );
    var sprite = new THREE.Sprite( spriteMaterial );
    sprite.scale.set(0.5 * fontsize, 0.25 * fontsize, 0.75 * fontsize);
    return sprite;  
}


function addNumbers(size, step)
{
	var spriteX, spriteY, spriteZ;
	for ( var i = -size; i <= size; i += step ) {

		if (i === 0){
			var sprite0 = makeTextSprite(String(i));
			scene.add(sprite0);
			sprite0.position.set(1, 1, 1);
		}
		else{
			spriteX = makeTextSprite(String(i));
			spriteY = spriteX.clone();
			spriteZ = spriteX.clone();
			scene.add(spriteX);
			scene.add(spriteY);
			scene.add(spriteZ);

			spriteX.position.set(i, 1, 1);
			spriteY.position.set(1, i, 1);
			spriteZ.position.set(1, 1, i);
		}
	}
}


document.getElementById('slider').oninput= function()
{
	var distance = document.getElementById('slider').value;
	var n = camera2.getWorldDirection();
	var coef = (n.x * n.y * n.z)/abs
	var m = n.multiplyScalar(-1 * distance);
	alert(m.x + "  " + m.y + "  " + m.z);
	camera2.position.copy(m);
}


function addGrid(size, step){

	var geometry = new THREE.Geometry();
	var material = new THREE.LineBasicMaterial( { vertexColors: THREE.VertexColors } );

	var grey = new THREE.Color( 0xbbbbbb );
	var black = new THREE.Color( 0x555555 );


	for ( var i = - size; i <= size; i += step ) {

		for ( var j = - size; j <= size; j += step ) {

			geometry.vertices.push(
				new THREE.Vector3( -size, j, i ), new THREE.Vector3( size, j, i ),
				new THREE.Vector3( i, -size, j ), new THREE.Vector3( i, size, j ),
				new THREE.Vector3( i, j, -size ), new THREE.Vector3( i, j, size )
			);

			//var color = (i === 0 && j === 0) ? color1 : color2;
			//geometry.colors.push( color, color, color, color, color, color );
			if (i === 0 && j === 0){
				var red = new THREE.Color( 0xff0000 );
				var green = new THREE.Color( 0x00ff00 );
				var blue = new THREE.Color( 0x0000ff );
				geometry.colors.push( red, red, green, green, blue, blue );
			}
			else{
				if (i === 0 || j === 0){
					geometry.colors.push( black, black, black, black, black, black );
				}
				else{
					geometry.colors.push( grey, grey, grey, grey, grey, grey );
				}
			}
		}

	}

	var grid = new THREE.LineSegments(geometry, material );
	scene.add(grid);
}

init();
animate();


function update_visibilities()
{
	for (var i_g = 0; i_g < group_count; i_g++){
		particleSystems[i_g].visible = (minThreshold <= i_g && i_g < maxThreshold);
	}
}
sliderMinElement.addEventListener('input', function () {
	minThreshold = sliderMinElement.value;
	update_visibilities()
}, false);

sliderMaxElement.addEventListener('input', function () {
	maxThreshold = sliderMaxElement.value;
	update_visibilities()
}, false);


function init() {


	// variables from "numbers.js" : NMK, R_arr, G_arr, B_arr, A_arr, X_arr, Y_arr, Z_arr
	var N = NMK[0];
	var M = NMK[1];
	var K = NMK[2];


	var maxPointSize = 1.4 * rarefaction;




	scene = new THREE.Scene();


	var container = document.getElementById( 'container' );

	renderer = new THREE.WebGLRenderer();
	renderer.setPixelRatio( window.devicePixelRatio ); //need to change, we don't look at window size anymore
	renderer.setSize( container.clientWidth, container.clientHeight );
	renderer.sortObjects = false;

	container.appendChild( renderer.domElement );

	camera = new THREE.PerspectiveCamera( 75, container.clientWidth / container.clientHeight, 0.1, 1000 );

	camera.position.z = NMK[0] * 2;


	controls = new THREE.TrackballControls( camera, renderer.domElement );
	//controls.addEventListener( 'change', render ); // add this only if there is no animation loop (requestAnimationFrame)
	controls.enableDamping = true;
	controls.dampingFactor = 0.25;
	controls.enableZoom = false;



	var for_plane = document.getElementById( 'for_plane' );

	renderer2 = new THREE.WebGLRenderer();
	//renderer2.setPixelRatio( window.devicePixelRatio );
	renderer2.setSize( for_plane.clientWidth,  for_plane.clientHeight );
	renderer2.domElement.style.position = 'absolute';
	for_plane.appendChild( renderer2.domElement );


	camera2 = new THREE.OrthographicCamera( -400, 400, -400, 400, 1, rarefaction );
	cam2_lookAt = new THREE.Vector3(500, 500, 500);
	camera2.lookAt(cam2_lookAt);
	//camera2.position.z = 0;
	//controls2 = new THREE.TrackballControls( camera2, renderer2.domElement );
	//controls2.target.set(300, 300, 300);


	
	particleSystems = [];
	for (var g_i = 0; g_i < group_count; g_i++){

		var	geometry = new THREE.BufferGeometry();

		var positions_int = points[g_i];
		var positions = new Float32Array( positions_int.length * 3 );	
		for (var i = 0; i < positions_int.length; i++){
			positions[i] =  positions_int[i];
		}
   		geometry.addAttribute( 'position', new THREE.BufferAttribute( positions, 3 ) );

   		var rgba = RGBA[g_i];
		var groupColor = new THREE.Color(rgba[0], rgba[1], rgba[2]);
		var pointsMaterial = new THREE.PointsMaterial({color:groupColor, size: rgba[3]*maxPointSize});
		var particleSystem = new THREE.Points( geometry ,pointsMaterial);

		particleSystems.push(particleSystem);
		scene.add(particleSystem);

	}
	update_visibilities()



	var my_plane_geom = new THREE.PlaneGeometry( 800, 800);
	my_plane_geom.position = camera2.position;
	my_plane_geom.quaternion = camera2.quaternion;
	var my_plane_mat = new THREE.MeshBasicMaterial( {color: 0x000000, side: THREE.DoubleSide,
													opacity: 0.3, transparent: true} );
	plane = new THREE.Mesh( my_plane_geom, my_plane_mat );
	scene.add( plane );
	scene.add( camera2 );


	addGrid(400, 200);
	addNumbers(400, 200);



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

	bind_plane_with_cam2();
	render();
	render2();

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


if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

//var stats;

var camera, controls, scene, renderer, uniforms, camera2, renderer2, controls2, plane, cam2_lookAt;
var particleSystems, minThreshold, maxThreshold;
var scene_is_empty = true;


var vis_area = document.getElementById( 'vis_area' );
var section_area = document.getElementById( 'section_area' );

var sliderElement = document.getElementById('slider');
var sliderXElement = document.getElementById('sliderX');
var sliderYElement = document.getElementById('sliderY');
var sliderZElement = document.getElementById('sliderZ');
var sliderMinElement = document.getElementById('sliderMin');
var sliderMaxElement = document.getElementById('sliderMax');
var sliderFiltration = document.getElementById('sliderF');
var sliderRarefaction = document.getElementById('sliderR');
var sliderNewRarefaction = document.getElementById('sliderNewR');



function sign(x) { return x < 0 ? -1 : 1; }

sliderElement.addEventListener('input', function () {
	var distance = sliderElement.value;
	var n = new THREE.Vector3();
	n.copy(cam2_lookAt);
	n.normalize();

	var coef = sign(n.x) * sign(n.y) * sign(n.z);
	n.multiplyScalar(  coef *  distance );
	camera2.position.copy(n);
	$("#plane_pos_val").text(sliderElement.value);
}, false);

sliderXElement.addEventListener('input', function () {
	cam2_lookAt.x = sliderXElement.value * 500;
	camera2.lookAt(cam2_lookAt);
	$("#plane_X_val").text(sliderXElement.value);
}, false);
sliderYElement.addEventListener('input', function () {
	cam2_lookAt.y = sliderYElement.value * 500;
	camera2.lookAt(cam2_lookAt);
	$("#plane_Y_val").text(sliderYElement.value);
}, false);
sliderZElement.addEventListener('input', function () {
	cam2_lookAt.z = sliderZElement.value * 500;
	camera2.lookAt(cam2_lookAt);
	$("#plane_Z_val").text(sliderZElement.value);
}, false);

function makeTextSprite( message, parameters )
{
    if ( parameters === undefined ) parameters = {};
    var fontface = parameters.hasOwnProperty("fontface") ? parameters["fontface"] : "Arial";
    var fontsize = parameters.hasOwnProperty("fontsize") ? parameters["fontsize"] : 70;
    var borderThickness = parameters.hasOwnProperty("borderThickness") ? parameters["borderThickness"] : 4;
    var borderColor = parameters.hasOwnProperty("borderColor") ? parameters["borderColor"] : { r:0, g:0, b:0, a:1.0 };
    var backgroundColor = parameters.hasOwnProperty("backgroundColor") ? parameters["backgroundColor"] : { r:255, g:255, b:255, a:1.0 };
    var textColor = parameters.hasOwnProperty("textColor") ? parameters["textColor"] : { r:0, g:0, b:0, a:1.0 };

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
//draw();
//animate();


function update_visibilities()
{
	for (var i_g = 0; i_g < group_count; i_g++){
		particleSystems[i_g].visible = (minThreshold <= i_g && i_g < maxThreshold);
	}
}

function big_num_repr(number)
{
	var result = number + " ";
	if (number >= 1000){
		if (number < 1000000){
			var rounded = Math.round(number / 100);
			var fractional = rounded % 10;
			var integral = Math.floor(rounded/10);
			result = integral + "." + fractional + "k"
		}
		else{
			var rounded = Math.round(number / 100000);
			var fractional = rounded % 10;
			var integral = Math.floor(rounded/10);
			result = integral + "." + fractional + "m"
		}
	}
	return result;
}

function estimate_new_point_count()
{
	var R = rarefaction;
	var newR = sliderNewRarefaction.value;
	var cur_point_count = COUNT[maxThreshold] - COUNT[minThreshold];

	var new_point_count = Math.round(cur_point_count * R*R*R / (newR*newR*newR));
	$("#n_p_cnt_val").text( big_num_repr(new_point_count) );
}

sliderMinElement.addEventListener('input', function () {
	minThreshold = +sliderMinElement.value;
	$("#lower_bound_val").text(minThreshold + "%");
	update_visibilities();
	//alert(minThreshold + "   " + maxThreshold);

	if (maxThreshold >= minThreshold){
		point_count = COUNT[maxThreshold] - COUNT[minThreshold];
		max_count = COUNT[group_count];
		$("#p_cnt_val").text(big_num_repr(point_count) + " / " + big_num_repr(max_count));
		estimate_new_point_count();
	}
}, false);

sliderMaxElement.addEventListener('input', function () {
	maxThreshold = +sliderMaxElement.value;
	$("#upper_bound_val").text(maxThreshold + "%");
	update_visibilities();
	//alert(minThreshold + "   " + maxThreshold);
	if (maxThreshold >= minThreshold){
		point_count = COUNT[maxThreshold] - COUNT[minThreshold];
		max_count = COUNT[group_count];
		$("#p_cnt_val").text(big_num_repr(point_count) + " / " + big_num_repr(max_count));
		estimate_new_point_count();
	}
}, false);

sliderFiltration.addEventListener('input', function () {
	$("#filtration_val").text(sliderFiltration.value);
}, false);
sliderRarefaction.addEventListener('input', function () {
	$("#rarefaction_val").text(sliderRarefaction.value);
}, false);
sliderNewRarefaction.addEventListener('input', function () {
	$("#new_rar_val").text(sliderNewRarefaction.value);
	estimate_new_point_count();
}, false);


function init() {


	// variables from "numbers.js" : NMK

	scene = new THREE.Scene();



	renderer = new THREE.WebGLRenderer();
	renderer.setPixelRatio( window.devicePixelRatio ); //need to change, we don't look at window size anymore
	renderer.setSize( vis_area.clientWidth, vis_area.clientHeight );
	renderer.sortObjects = false;
	//alert();

	vis_area.appendChild( renderer.domElement );
	renderer.domElement.style.visibility = "hidden";
	camera = new THREE.PerspectiveCamera( 75, vis_area.clientWidth / vis_area.clientHeight, 0.1, 2000 );


	controls = new THREE.TrackballControls( camera, renderer.domElement );
	//controls.addEventListener( 'change', render ); // add this only if there is no animation loop (requestAnimationFrame)
	controls.enableDamping = true;
	controls.dampingFactor = 0.25;
	controls.enableZoom = false;




	renderer2 = new THREE.WebGLRenderer();
	renderer2.setSize( section_area.clientWidth,  section_area.clientHeight );
	renderer2.domElement.style.position = 'absolute';
	section_area.appendChild( renderer2.domElement );

	


	var my_plane_geom = new THREE.PlaneGeometry( 800, 800);
	var my_plane_mat = new THREE.MeshBasicMaterial( {color: 0x000000, side: THREE.DoubleSide,
													opacity: 0.3, transparent: true} );
	plane = new THREE.Mesh( my_plane_geom, my_plane_mat );
	//scene.add( plane );
	//scene.add( camera2 );


	//addGrid(400, 200);
	//addNumbers(400, 200);


	//window.addEventListener( 'resize', onWindowResize, false );
	alert("Draw!");

}

function draw() {

	var N = NMK[0];
	var M = NMK[1];
	var K = NMK[2];


	var maxPointSize = 1.4 * rarefaction;
	camera.position.z = NMK[0] * 2;

	camera2 = new THREE.OrthographicCamera( -400, 400, -400, 400, 1, (rarefaction  + 1)/2);
	cam2_lookAt = new THREE.Vector3(500, 500, 500);
	camera2.lookAt(cam2_lookAt);


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
	update_visibilities();
	scene_is_empty = false;
}

function onWindowResize() {
	//need to change, also we don't look at window size anymore
	camera.aspect = vis_area.innerWidth / vis_area.innerHeight;
	camera.updateProjectionMatrix();

	renderer.setSize( vis_area.innerWidth, vis_area.innerHeight );

}

function animate() {

	requestAnimationFrame( animate );

	//controls.update(); // required if controls.enableDamping = true, or if controls.autoRotate = true
	//controls2.update(); // required if controls.enableDamping = true, or if controls.autoRotate = true
	controls.update();
	//stats.update();

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

var SERVER_URI = "http://localhost:5001"

function get_draw(filename){	
	$.ajax({
		url: SERVER_URI + "/take_json/" + filename,
		async: false,
		method: 'GET',
		cache: false,
		dataType: 'json',
		success: function(data, status){
			$("#default_text").css('display', 'none');
			renderer.domElement.style.visibility = "visible";
			alert("success");
			if (scene_is_empty == false){
				for (var g_i = 0; g_i < group_count; g_i++){
					scene.remove(particleSystems[g_i]);
				}
			}
			group_count = data["group_count"];
			NMK = data["NMK"];
			points = data["points"];
			RGBA = data["RGBA"];
			rarefaction = data["rarefaction"];
			COUNT = data["COUNT"];


			minThreshold = group_count * 0.75, maxThreshold = group_count;
			sliderMinElement.max = group_count;
			sliderMaxElement.max = group_count;
			sliderMinElement.defaultValue = minThreshold;
			sliderMaxElement.defaultValue = maxThreshold;

			draw();
			animate();
		},
			  
		error: function(xhr, status, error) {
			alert(error);
			var err = eval("(" + xhr.responseText + ")");
			alert(err.Message);
		},
			//complete: function(jqXHR, status){ alert("complete!"); alert(status); alert( jqXHR.responseText);  }
	});

}

$("#btn_Apply").click(function(event){
	var filename = "F" + sliderFiltration.value + "R" + sliderRarefaction.value + ".json";
	alert("waiting for data...");
	get_draw(filename);
});

$("#btn_Cut").click(function(event){

	alert("waiting for data...");

	$.ajax({
		url: SERVER_URI + "/cut/" + sliderFiltration.value + '/' + sliderNewRarefaction.value + '/' + (Math.round(sliderMinElement.value * 100/group_count)) + '/' + (Math.round(sliderMaxElement.value*100/group_count)),
		async: false,
		method: 'GET',
		cache: false,
		success: function(data, status){
			$("#default_text").css('display', 'none');
			renderer.domElement.style.visibility = "visible";
			alert("success");
			if (scene_is_empty == false){
				for (var g_i = 0; g_i < group_count; g_i++){
					scene.remove(particleSystems[g_i]);
				}
			}
			group_count = data["group_count"];
			NMK = data["NMK"];
			points = data["points"];
			RGBA = data["RGBA"];
			rarefaction = data["rarefaction"];
			COUNT = data["COUNT"];


			minThreshold = group_count * 0.75, maxThreshold = group_count;
			sliderMinElement.max = group_count;
			sliderMaxElement.max = group_count;
			sliderMinElement.defaultValue = minThreshold;
			sliderMaxElement.defaultValue = maxThreshold;

			draw();
			animate();
		},
			  
		error: function(xhr, status, error) {
			alert(error);
			var err = eval("(" + xhr.responseText + ")");
			alert(err.Message);
		},
			//complete: function(jqXHR, status){ alert("complete!"); alert(status); alert( jqXHR.responseText);  }
	});
		//*/
});
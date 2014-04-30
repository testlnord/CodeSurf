#ifdef GL_ES
precision mediump float;
#endif

uniform float time;
uniform vec2 resolution;
uniform float r;
uniform float g;
uniform float b;

float addColor(float prevColor, float x, float y, float time, float size, float offset, float speed){
	return min(1., prevColor + size * sin(sqrt(x*x+y*y)*3.14 + offset + time * speed) / (sqrt (x*x+y*y) * 3.14));
}

void main( void ) {

	vec2 position = gl_FragCoord.xy / resolution.xy;
	float x = position.x - .1;
	float y = position.y - .4;
	float color = 0.0;
	color = addColor(color, x, y, time, .7, 1.1, 1.);

	x -= .5;
	color = addColor(color, x, y, time, .5, 2., 1.2);

	y -= .45;
	x -= -.1;
	color = addColor(color, x, y, time, .85, 3., .9);
	x -= .3;
	y += .2;
	color = addColor(color, x, y, time, .2, .4, 1.6);

	x = position.x - .4;
	y = position.y - .3;
	color = addColor(color, x, y, time, .1, .14, 1.9);

	x = position.x - .9;
	y = position.y - .9;
	color = addColor(color, x, y, time, .9, .13, .5);

	gl_FragColor = vec4( vec3( max(.15,color * r), max(.09, color * g), max(.07, color * b)), 1.0 );

}

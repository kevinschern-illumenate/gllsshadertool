//Basic fractal by @paulofalcao

 


// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

int maxIterations=iComplexity+1;//a nice value for fullscreen is 8

float circleSize=1.0/(3.0*pow(2.0,float(maxIterations)));

//generic rotation formula
vec2 rot(vec2 uv,float a){
	return vec2(uv.x*cos(a)-uv.y*sin(a),uv.y*cos(a)+uv.x*sin(a));
}

void mainImage( out vec4 fragColor, in vec2 fragCoord ){
	//normalize stuff
	

	vec2 uv = ((fragCoord.xy / iResolution.xy)-0.5)*1.5;
	if(iResolution.x < iResolution.y)
	{
		uv.x *= iResolution.x/iResolution.y;
	}
	else
	{
		uv.y *= iResolution.y/iResolution.x;
	}

	//global rotation and zoom
	uv=rot(uv,LOOP_TIME*1.0);
	//uv*=sin(LOOP_TIME*1.0)*0.5+1.5;
	
	//mirror, rotate and scale 6 times...
	float s=0.3;
	for(int i=0;i<maxIterations;i++){
		uv=abs(uv)-s;
		uv=rot(uv,LOOP_TIME*1.0);
		s=s/2.1;
	}
	
	//draw a circle
	float c=length(uv)>circleSize?0.0:1.0;	

	fragColor = vec4(c,c,c,1.0);
}
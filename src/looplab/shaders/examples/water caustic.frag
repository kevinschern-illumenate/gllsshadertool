// Found this on GLSL sandbox. I really liked it, changed a few things and made it tileable.
// :)
// by David Hoskins.


// Water turbulence effect by joltz0r 2013-07-04, improved 2013-07-07


// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

#define iBaseHueRad 3.46

// Redefine below to see the tiling...
//#define SHOW_TILING

#define TAU 6.28318530718
float MAX_ITER = iComplexity + 2;

void mainImage( out vec4 fragColor, in vec2 fragCoord ) 
{
	float time = LOOP_TIME*1.0+23.0;
    // uv should be the 0-1 uv of texture...
	

	vec2 uv = fragCoord.xy / iResolution.xy-0.5;
	if(iResolution.x < iResolution.y)
	{
		uv.x *= iResolution.x/iResolution.y;
	}
	else
	{
		uv.y *= iResolution.y/iResolution.x;
	}
    
#ifdef SHOW_TILING
	vec2 p = mod(uv*TAU*2.0, TAU)-250.0;
#else
    vec2 p = mod(uv*TAU, TAU)-250.0;
#endif
	vec2 i = vec2(p);
	float c = 1.0;
	float inten = .005;	
	for (int n = 0; n < MAX_ITER; n++) 
	{
		float t = time * (1.0 - (3.5 / float(n+1)));
		i = p + vec2(cos(t - i.x) + sin(t + i.y), sin(t - i.y) + cos(t + i.x));
		c += 1.0/length(vec2(p.x / (sin(i.x+t)/inten),p.y / (cos(i.y+t)/inten)));
	}
	c /= float(MAX_ITER);
	c = 1.17-pow(c, 1.4);
	vec3 colour = vec3(pow(abs(c), 8.0));
    
    
    if(mColorMode != 1)
    {
		colour = clamp(colour + vec3(0.0, 0.35, 0.5), 0.0, 1.0);    	
    }
    else
    {
    	colour = clamp(colour + vec3(0.5), 0.0, 1.0);
    } 

	#ifdef SHOW_TILING
	// Flash tile borders...
	vec2 pixel = 2.0 / iResolution.xy;
	uv *= 2.0;

	float f = floor(mod(LOOP_TIME*1.0, 2.0)); 	// Flash value.
	vec2 first = step(pixel, uv) * f;		   	// Rule out first screen pixels and flash.
	uv  = step(fract(uv), pixel);				// Add one line of pixels per tile.
	colour = mix(colour, vec3(1.0, 1.0, 0.0), (uv.x + uv.y) * first.x * first.y); // Yellow line
	
	#endif
	fragColor = vec4(colour, 1.0);
}
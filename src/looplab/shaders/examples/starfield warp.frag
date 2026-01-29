


// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

const float tau = 6.28318530717958647692;
#define iBaseHueRad 3.8

// Gamma correction
#define GAMMA (2.2)

vec3 ToLinear( in vec3 col )
{
	// simulate a monitor, converting colour values into light values
	return pow( col, vec3(GAMMA) );
}

vec3 ToGamma( in vec3 col )
{
	// convert back into colour values, so the correct light will come out of the monitor
	return pow( col, vec3(1.0/GAMMA) );
}

vec4 Noise( in ivec2 x )
{
	return texture( iChannel0, (vec2(x)+0.5)/256.0, -100.0 );
}

vec4 Rand( in int x )
{
	vec2 uv;
	uv.x = (float(x)+0.5)/256.0;
	uv.y = (floor(uv.x)+0.5)/256.0;
	return texture( iChannel0, uv, -100.0 );
}


void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
	vec3 ray;
	//ray.xy = 2.0*(fragCoord.xy-iResolution.xy*.5)/iResolution.x;

	ray.xy = (fragCoord.xy / iResolution.xy-0.5)*1.0;
	if(iResolution.x < iResolution.y)
	{
		ray.x *= iResolution.x/iResolution.y;
	}
	else
	{
		ray.y *= iResolution.y/iResolution.x;
	}

	ray.z = 1.0;

	float offset = LOOP_TIME*1.0*0.3;	
	float speed2 = (0.5+1.0)*2.0;
	float speed = speed2+.1;
	offset += 0.5*.96;
	offset *= 2.0;
	
	
	vec3 col = vec3(0);
	
	vec3 stp = ray/max(abs(ray.x),abs(ray.y));
	
	vec3 pos = 2.0*stp+.5;
	float power = pow(iForce/5.5, 2.8)+0.4;
	float count = pow(2., 0.+iComplexity);
	for ( float i=0.; i < count; i++ )
	{
		float z = Noise(ivec2(pos.xy)).x;
		z = fract(z-offset);
		float d = 50.0*z-pos.z;
		float w = pow(max(0.0,1.0-8.0/power*length(fract(pos.xy)-.5)),2.0)*2.0;
		vec3 c = max(vec3(0),vec3(1.0-abs(d+speed2*.5)/speed,1.0-abs(d)/speed,1.0-abs(d-speed2*.5)/speed));
		col += 1.5*(1.0-z)*c*w;
		pos += stp;
	}
	
	fragColor = vec4(ToGamma(col),1.0);
}
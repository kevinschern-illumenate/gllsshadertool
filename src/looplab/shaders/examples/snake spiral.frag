// https://www.shadertoy.com/view/NsXyDX


// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

int calcSnake(ivec2 pos) {
    int x = pos.x; int y = pos.y;
    int res0 = (x * (x - 1) * 4 + 3 * x) + ((x < 0) ? -2*x  +y : -y);
    int res1 = (y * (y - 1) * 4 + 1 * y) + ((y < 0) ?  2*y  -x : +x);
    return max(res0, res1);
}

float calcCol(vec2 uv) {
    float f = float(calcSnake(ivec2(uv)));   
    return fract(f / 240. - LOOP_TIME / 12.);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    // Normalized pixel coordinates (from 0 to 1)
	
	vec2 p = (fragCoord.xy / iResolution.xy-0.5);
    if(iResolution.x < iResolution.y)
    {
        p.x *= iResolution.x/iResolution.y;
    }
    else
    {
        p.y *= iResolution.y/iResolution.x;
    }
	
    
    
    p = floor(p * 40.);   

    float c = calcCol(p);
    // Output to screen
	
	
	float power = pow((11.-iForce)/4.0, 3.)*10.;
    fragColor = vec4(pow(c, power));
    
}
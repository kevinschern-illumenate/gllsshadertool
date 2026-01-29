//#define colorRGB vec3

// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

#define colorRGBA vec4
uniform float iHueShiftRad;	// enable hue shift param

const float lineScale = 12.0;
//Got inspiration/learning from this guys effect. 
//I took time to learn how he did/what he did and tried to make a simplifed version that I could actually make without just copy pasting his work 
//Still Credits to:TheOnlyaaa
//http://glslsandbox.com/e#40822.0
//Full Screen Effect
float Cube(vec2 pos)
{
    float radius = atan(pos.x, pos.y);
float num = abs(pos.x) + abs(pos.y);
    //float num = length(pos);
    float curLine = floor(num * lineScale);
    float speed = sin(curLine * 24.3);
    float offset = fract(sin(speed));
   
	float power = pow((11.0-iForce)/5.5, 3.)*2.+0.1;
    float c = step(power, tan(radius + offset + speed * LOOP_TIME ));
   
    float rnd = offset;
    return c * rnd;
}

 vec4 rotatingDiamonds(float a,float b,out vec4 fragColor, in vec2 fragCoord)
 {
     vec2 uv = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
     vec4 finalOutput = vec4(Cube(uv), Cube(uv - a), Cube(uv), b);
     return finalOutput;
 }

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{

	float power = pow(iForce2/5.5, 3.)*0.02+0.0;
    fragColor = rotatingDiamonds(power,10.0, fragColor, fragCoord);
}


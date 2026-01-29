// Whitney Music Box - Jim Bumgardner
// whitneymusicbox.org


// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

const float rad = 0.6;
float dots = iComplexity*10.0;
const float duration = 180.0;
const vec3 colorsep = vec3(0,2.09,4.18);
const float PI = 3.1415926535897932384626433832795;
const float PI2 = 2.0*3.1415926535897932384626433832795;

void mainImage( out vec4 fragColor, in vec2 fragCoord ) {
  //vec2 p = -1.0 + 2.0 * fragCoord.xy / iResolution.xy;
  float tm = (LOOP_TIME+20.)*0.005;
  //p.y *= iResolution.y/iResolution.x;

   vec2 p = (fragCoord.xy / iResolution.xy-0.5)*1.5;
  if(iResolution.x < iResolution.y)
  {
    p.x *= iResolution.x/iResolution.y;
  }
  else
  {
    p.y *= iResolution.y/iResolution.x;
  }

  vec3 gradient = vec3(0.0);

  for (float i=1.0; i<=dots; i++)
  {
    float i2pi = i*PI2;
    float ang = mod(tm*i2pi*0.2, PI2);
    float ang2 = mod(tm*i2pi*1.5, PI2);
    float amp = rad*(1.0-(i-1.0)/dots);
    float cang = i2pi/dots;
    //float fade = 0.7 - pow(smoothstep(0.0,1.0,ang),2.0)*0.5;
    float power = pow(iForce/5.5, 3.);
    float fade = 0.5 + power*0.1 * tan(ang);
    vec2 star_pos = vec2(cos(ang2) * amp, -sin(ang2) * amp);
    gradient += (cos(cang+colorsep) + 1.0/2.0) * ((fade / 384.0) / pow(length(star_pos - p), 1.5)) * fade;
  }
  fragColor = vec4( gradient, 1.0);
}
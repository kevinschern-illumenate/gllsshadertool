
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

// by @etiennejcb
// Using Ikeda style pattern from bookofshaders : https://thebookofshaders.com/edit.php#10/ikeda-03.frag
// Using torus raymarching from https://www.shadertoy.com/view/MsX3Wj

// There is some antialiasing
const bool TURN_ON_ANTI_ALIASING = true; // put it to false for faster computation

const float PI = 3.14159265358979323846264;
const int MAX_PRIMARY_RAY_STEPS = 30; // decrease this number if it runs slow on your computer


const vec2 c = vec2(1.,0.);

float sdTorus( vec3 p, vec2 t ) {
  vec2 q = vec2(length(p.xz)-t.x,p.y);
  return length(q)-t.y;
}

float distanceField(vec3 p) {
    return -sdTorus(p.yxz, vec2(5.0, 1.0));
}

vec3 castRay(vec3 pos, vec3 dir) {
    for (int i = 0; i < MAX_PRIMARY_RAY_STEPS; i++) {
            float dist = distanceField(pos);
            pos += dist * dir;
    }
    return pos;
}


float rand(vec2 a0)
{
    return fract(sin(dot(a0.xy ,vec2(12.9898,78.233)))*43758.5453);
}

float random(float x)
{
    float r1 = -1.+2.*rand(floor(x)*c.xx), r2 = -1.+2.*rand(ceil(x)*c.xx);
    return mix(r1, r2, smoothstep(.25, .75, fract(x)));
}

float random (in vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898,78.233)))* 43758.5453123);
}

float pattern(vec2 st, vec2 v, float t) {
    vec2 p = floor(st+v);
    return step(t, random(25.+p*.000004)+random(p.x)*0.75 );
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    fragColor = vec4(0.0);

    
    
    for(float di=-0.25;di<=0.25;di+=.5){
        for(float dj=-0.25;dj<=0.25;dj+=.5){
            
            vec2 screenPos = ((fragCoord.xy + vec2(di,dj)) / iResolution.xy) * 2.0 - 1.0;
            vec3 cameraPos = vec3(0.0, 4.2, -3.8);

            vec3 cameraDir = vec3(0., 0.22, 1.3);
            vec3 planeU = vec3(1.0, 0.0, 0.0) * 0.8;
            vec3 planeV = vec3(0.0, iResolution.y / iResolution.x * 1.0, 0.0);
            vec3 rayDir = normalize(cameraDir + screenPos.x * planeU + screenPos.y * planeV);

            vec3 rayPos = castRay(cameraPos, rayDir);

            float majorAngle = atan(rayPos.z, rayPos.y);
            float minorAngle = atan(rayPos.x, length(rayPos.yz) - 5.0);

            vec2 st = vec2(majorAngle/PI/2.0,minorAngle/PI);

            vec2 grid = vec2(iNbItems*2.+5.,iNbItems2*2.0);
            st *= grid;

            vec2 ipos = floor(st);  // integer
            vec2 fpos = fract(st);  // fraction

            vec2 vel = vec2(LOOP_TIME*1.0*max(grid.x,grid.y)); // time
            vel *= vec2(1.,0.0) *(0.4+2.0*pow(random(1.0+ipos.y),2.0)); // direction

           

            float force = 1.5 - iForce / 8.0;
            float color = pattern(st,vel,force);
            
            if(TURN_ON_ANTI_ALIASING){
                fragColor += 0.25*vec4(color);
            } else {
                fragColor = vec4(color);
                return;
            }
        }
    }
}
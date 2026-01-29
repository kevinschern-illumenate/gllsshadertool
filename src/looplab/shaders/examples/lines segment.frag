

// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

float time = LOOP_TIME*2.0;

vec3 mod289(vec3 x) {
  return x - floor(x * (1.0 / 289.0)) * 289.0;
}
vec2 mod289(vec2 x) {
  return x - floor(x * (1.0 / 289.0)) * 289.0;
}
vec3 permute(vec3 x) {
  return mod289(((x*34.0)+1.0)*x);
}
float snoise(vec2 v)
{
    const vec4 C = vec4(0.211324865405187,
                      0.366025403784439,
                     -0.577350269189626,
                      0.024390243902439);
    vec2 i  = floor(v + dot(v, C.yy) );
    vec2 x0 = v -   i + dot(i, C.xx);
    vec2 i1;
    i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
    vec4 x12 = x0.xyxy + C.xxzz;
    x12.xy -= i1;
    i = mod289(i);
    vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 ))
            + i.x + vec3(0.0, i1.x, 1.0 ));
    vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy), dot(x12.zw,x12.zw)), 0.0);
    m = m*m ;
    m = m*m ;
    vec3 x = 2.0 * fract(p * C.www) - 1.0;
    vec3 h = abs(x) - 0.5;
    vec3 ox = floor(x + 0.5);
    vec3 a0 = x - ox;
    m *= 1.79284291400159 - 0.85373472095314 * ( a0*a0 + h*h );
    vec3 g;
    g.x  = a0.x  * x0.x  + h.x  * x0.y;
    g.yz = a0.yz * x12.xz + h.yz * x12.yw;
    return 130.0 * dot(m, g);
}
float d_seg(vec2 position, vec2 start_p, vec2 end_p)
{  
    vec2 AP = position - start_p;
    vec2 AB = end_p - start_p;
    float h = clamp(dot(AP, AB) / dot(AB, AB), 0.0, 1.0);
    float seg = length(AP - AB * h);
    return seg;
}
void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 position = (fragCoord.xy / iResolution.xy-0.5) * 7.0;   

    float power = pow(iForce/5.5, 2.) * 0.09;
    vec4 color = vec4(0.2,0.2,0.2,1.0);
    float light = 0.0, line;
    int num = (iComplexity-1) * 3 + 5;
    vec2 points[25+1];
    vec2 sn_p1 = 1.0*time * vec2(1.0, 0.8);
    vec2 sn_p2 = 1.0*time * vec2(0.9, 1.1);
    points[num] = points[0] = 4.0 * vec2(snoise(sn_p1), snoise(sn_p2));
    for(int i = 1; i < num; i++)
    {
        points[i] = 4.0 * vec2(snoise(sn_p1 + float(i) * vec2(1.0, 1.4)), snoise(sn_p2 + float(i) * vec2(0.8, 1.2)));
        line = d_seg(position, points[i-1], points[i]);
        light += power / line;
    }
    

    line = d_seg(position, points[num-1], points[num]);
    
    light += power / line;
    
    fragColor = color * light; 
}
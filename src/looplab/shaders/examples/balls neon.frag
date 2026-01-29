
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

uniform float iHueShiftRad;	// enable hue shift param 
 

float stepping(float t){
    if(t<0.)return -1.+pow(1.+t,2.);
    else return 1.-pow(1.-t,2.);
}
void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
      vec2 uv = (fragCoord.xy / iResolution.xy-0.5)*2.0;
    if(iResolution.x < iResolution.y)
    {
        uv.x *= iResolution.x/iResolution.y;
    }
    else
    {
        uv.y *= iResolution.y/iResolution.x;
    }
    fragColor = vec4(0);
    float time = LOOP_TIME*1.0 + 4.141592/3.;
    float count = pow(2., 0.+iComplexity);
    uv = normalize(uv) * length(uv);
    for(int i=0;i<count;i++){
        float t = time + float(i)*3.141592/12.*(5.+1.*stepping(sin(time*3.)));
        vec2 p = vec2(cos(t),sin(t));
        p *= cos(time + float(i)*3.141592*cos(time/8.));
        vec3 col = cos(vec3(0,1,-1)*3.141592*2./3.+3.141925*(time/2.+float(i)/5.)) * 2.9 * iForce/5. + 0.5;
        fragColor += vec4(0.05/length(uv-p*0.9)*col,1.0);
    }
    fragColor.xyz = pow(fragColor.xyz,vec3(3.));
    fragColor.w = 1.0;
}
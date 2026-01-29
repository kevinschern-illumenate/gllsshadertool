// original https://www.shadertoy.com/view/MddSzl# by Andre
// https://www.shadertoy.com/view/MltSRn

float freqs[4];

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
	vec2 uv1 = (fragCoord.xy-iResolution.xy*.5) / iResolution.y;
    vec2 uv = uv1*4.0;
    
    freqs[0] = 0.;
	freqs[1] = iAudioRMS*iForce;
	freqs[2] = 0.;
	freqs[3] = iAudioMid*iForce/15.0;
    
    float c = 1.;
    uv.x = abs(uv.x);
    uv.x -= 1.;
    float gt = (iTime+200.)*(1.3+freqs[1]*0.01);
    float nbIters = iComplexity * 30;
    for (float i = 0.0; i< nbIters; i++) {
      gt += i*.72;
      c *= min(0.1+max(freqs[3]*2.-0.1,1.),distance(uv,
                            vec2(sin(gt*0.2)+cos(gt*(i/57.))
                                ,sin(gt*0.08)+cos(gt*(i/93.)))));
    }
    
	fragColor = vec4(clamp(
                       mix( vec3(10.0),
                            vec3(.10),
                            smoothstep(.1,0.12,c))
                       *(0.9+0.
                       *.25*max(-.2,4.0-length(uv)))
                       ,0.0,1.0)
                     ,1.0);
    vec2 position = (fragCoord.xy / iResolution.xy) - vec2(0.5);
    float vignette = smoothstep(0.9, 0.1+freqs[1]/5., length(position));
    fragColor = vec4(fragColor.xyz * vignette, 1.0);
    
    
}
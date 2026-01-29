/*
2D LED Spectrum - Visualiser
Based on Led Spectrum Analyser by: simesgreen - 27th February, 2013 https://www.shadertoy.com/view/Msl3zr
2D LED Spectrum by: uNiversal - 27th May, 2015
Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
https://www.shadertoy.com/view/4sdGDM
*/

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    // create pixel coordinates
    vec2 uv = fragCoord.xy / iResolution.xy;

    // quantize coordinates
    float bands = iNbItems;
    float segs = iNbItems2;
    vec2 p;
    p.x = floor(uv.x*bands)/bands;
    p.y = floor(uv.y*segs)/segs;

    // read frequency data from first row of texture
    float fft  = texture( iAudioSamples, vec2(p.x,0.5) ).x;
   
    // led color
    vec3 color = mix(vec3(2.0, 2.0, 2.0), vec3(2.0, 2.0, 2.0), sqrt(uv.y));

    float power = iForce / 5.5 * 0.1;
    // mask for bar graph
   float mask = (p.y < fft+power) ? 1.0 : 0.0;

         mask*= (p.y > fft-power) ? 1.0 : 0.0;
      
    // led shape
    vec2 d = fract((uv - p) *vec2(bands, segs)) - 0.5;
    float led = smoothstep(0.5, 0.35, abs(d.x)) *
                smoothstep(0.5, 0.35, abs(d.y));
    vec3 ledColor = led*color*mask;

    // output final color
     
    fragColor = vec4(ledColor, 1.0);
    
}

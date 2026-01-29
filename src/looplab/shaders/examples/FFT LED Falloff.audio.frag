/*
2D LED Spectrum - Visualiser
Based on Led Spectrum Analyser by: simesgreen - 27th February, 2013 https://www.shadertoy.com/view/Msl3zr
2D LED Spectrum by: uNiversal - 27th May, 2015
Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
https://www.shadertoy.com/view/Mlj3WV
*/

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    // create pixel coordinates
    vec2 uv = fragCoord.xy / iResolution.xy;
    uv.y = abs(uv.y);
    // quantize coordinates
    float bands = iNbItems;
    
    vec2 p;
    p.x = floor(uv.x*bands)/bands;
    p.y = uv.y;
    
    float fft  = texture( iAudioFFT, vec2(p.x,0.0) ).x*pow(iForce/5.5,2.0);

    // led color
    vec3 color = vec3(1.0);
    
    float ledShapeForce = pow(iForce2/20.0, 2.0);    
    
    // led shape
    float vertDistanceToFFT = pow(max(0,1.0 - abs(fft-p.y) / ledShapeForce), 0.5);
    vec3 ledColor = color*vertDistanceToFFT;

    // output final color
    fragColor = vec4(ledColor, 1.0);
}

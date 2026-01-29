

#define iBaseHueRad 5.13

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord.xy / iResolution.xy;
    uv.y = abs(uv.y);
    vec2 c0xy = vec2(uv.x, 0.25);

    float c0 = texture(iAudioFFT, c0xy).x*pow(iForce/5.5, 3.0);
 
    vec4 color = vec4(1.0, 1.0, 1.0, 1.0);
    
    if (uv.y > c0) {
        c0 += 0.05;
        color = vec4(c0, uv.x, 1.0, 1.0);
        color.rgb -= (uv.y - c0) * 10.0;
    }

    fragColor = color;
}
void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord/iResolution.xy;
    uv.y *= 2.; uv.y -= 1.;
	
    float a = texture(iAudioFFT, vec2( uv.x, 0.)).x*pow(iForce/5.5, 3.0)*1.5;

    float c = abs(uv.y) < a ? a : 0.;

    fragColor = vec4(vec3(c), 1.0);
}
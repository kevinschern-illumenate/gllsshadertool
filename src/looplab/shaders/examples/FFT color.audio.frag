float rand(vec2 n) { 
	return fract(sin(dot(n, vec2(12.9898, 4.1414))) * 43758.5453);
}

// Hat function centered in c.
float hat(float x, float c) {
	return max(1.0-abs(x-c), 0.0);
}


vec3 mix_colors(vec3 c0, vec3 c1, vec3 c2, float f) {
	return c0 * hat(f, 0.0) + c1 * hat(2.0*f, 1.0) + c2 * hat(f, 1.0);
}


void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    float time = iTime;
 
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = fragCoord/iResolution.xy;
    vec2 mouse = iMouse.xy/iResolution.xy;
    //uv.x += (rand(uv*time+i)- 0.5) * 0.01;

    //uv.x = abs(2.0*uv.x-1.0);


    // Frequency.
    float fft = texture(iAudioFFT, vec2(uv.x*uv.x*uv.x, 0.25)).x;
    fft = pow(fft, 4.0);
    //fft = smoothstep(0.4, 1.0, fft);
    fft *= 9.0 * pow(iForce/5.5, 3.0);


    // Volume.
    // float vol = texture(iAudio, vec2(uv.x, 0.75)).x;

    vec3 col = vec3(1.0) * abs(fft);
    col *= hat(2.0*uv.y, 1.0); // vertically center the plot

    vec3 low  = vec3(1.0, 0.0, 0.0);
    vec3 mid  = vec3(0.0, 1.0, 0.0);
    vec3 high = vec3(0.0, 0.0, 1.0);
    col *= mix_colors(low, mid, high, uv.x*uv.x); // color based on x coordinate (frequency)

    fragColor = vec4(col,1.0);
}
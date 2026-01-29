

#define iBaseHueRad 5.78

vec3 COLOR1 = vec3(0.0, 0.0, 0.3);
vec3 COLOR2 = vec3(0.5, 0.0, 0.0);
float BLOCK_WIDTH = 0.01;
void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord.xy / iResolution.xy;
    
    // To create the BG pattern
    vec3 final_color = vec3(1.0);
    vec3 bg_color = vec3(0.0);
    vec3 wave_color = vec3(0.0);
    
    float c1 = mod(uv.x, 2.0 * BLOCK_WIDTH);
    c1 = step(BLOCK_WIDTH, c1);
    
    float c2 = mod(uv.y, 2.0 * BLOCK_WIDTH);
    c2 = step(BLOCK_WIDTH, c2);
    
    bg_color = mix(uv.x * COLOR1, uv.y * COLOR2, c1 * c2);
    
    
    // To create the waves
    float wave_width = 0.01;
    uv  = -1.0 + 2.0 * uv;
    uv.y += 0.1;
    
       // create pixel coordinates
    //vec2 uv = fragCoord.xy / iResolution.xy;

    
    vec2 uvo = uv;
    uv = fragCoord.xy / iResolution.xy;
    
    // first texture row is frequency data
    float fft  = texture( iAudioFFT, vec2(uv.x,0.25) ).x*pow(iForce/5.5, 3.0); 
    
    // second texture row is the sound wave
    float wave = texture( iAudioSamples, vec2(uv.x,0.75) ).x;
    
    // convert frequency to colors
    vec3 col = vec3( fft, 4.0*fft*(1.0-fft), 1.0-fft ) * fft;

    // add wave form on top 
    col += 1.0 -  smoothstep( 0.0, 0.15, abs(wave - uv.y) );
    
    // output final color
    //fragColor = vec4(col,1.0);
    uv = uvo;
    
    float nbIters  = iComplexity * 3.0;
    for(float i = 0.0; i < nbIters; i++) {
        
        uv.y += (0.07 * sin(uv.x + (i*(fft*wave))/7.0 + (iTime + (wave*(1.0+fft))))) ;
        wave_width = abs(1.0 / (150.0 * uv.y));
        wave_color += vec3(wave_width * 1.9, wave_width, wave_width * 1.5);
    }
    
    bg_color.x *= sin(wave*cos(fft)/iTime);
    bg_color.z *= cos(fft*sin(wave))*col.z;
    
    final_color = bg_color + wave_color;
    final_color *= (0.75 * (1.0+(fft*(10.0/wave))));
//  final_color -= (col - wave);
    vec3 inv = final_color - (col - wave);
    
   final_color = final_color * 0.075 * (inv * 0.75);
    
    fragColor = vec4(final_color, 1.0);
}
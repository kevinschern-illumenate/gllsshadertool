// https://www.shadertoy.com/view/4lyBRV

vec3 COL1 = vec3(1.0);
vec3 COL2 = vec3(1.0);

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord.xy/iResolution.xy;

    
    float grid = float(mod(floor(uv.x * 500.0),14.0) < 0.5);
    grid += float(mod(floor(uv.y * 200.0),11.0) < 0.5); 
    grid = float(grid>0.5);
    
    vec2 uvn = 2.0 * uv - 1.0;
  
    // aquire wave
    float wa = texture(iAudioSamples,vec2(uv.x,0.75)).x*pow(iForce/5.5, 2.0);
    
    //atenuate
    float i = pow(1.0-abs(uv.y-wa+(pow(iForce/5.5, 2.0)-1.0)/2.0),20.0);
    vec3 col = vec3(i) * mix(COL1,COL2,i);
    fragColor = vec4(col,1.0);
}

// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

// ---- change here ----
const float USE_KALEIDOSCOPE = 1.0;
float NUM_SIDES = iComplexity+1.0;

// math const
const float PI = 3.14159265359;
const float DEG_TO_RAD = PI / 180.0;

// -4/9(r/R)^6 + (17/9)(r/R)^4 - (22/9)(r/R)^2 + 1.0
float field( vec2 p, vec2 center, float r ) {
    float d = length( p - center ) / r;
    
    float t   = d  * d;
    float tt  = t  * d;
    float ttt = tt * d;
    
    float v =
        ( - 4.0 / 9.0 ) * ttt +
        (  17.0 / 9.0 ) * tt +
        ( -22.0 / 9.0 ) * t +
        1.0;
    
    return clamp( v, 0.0, 1.0 );
}

vec2 Kaleidoscope( vec2 uv, float n, float bias ) {
    float angle = PI / n;
    
    float r = length( uv );
    float a = atan( uv.y, uv.x ) / angle;
    
    a = mix( fract( a ), 1.0 - fract( a ), mod( floor( a ), 2.0 ) ) * angle;
    
    return vec2( cos( a ), sin( a ) ) * r;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = (fragCoord.xy / iResolution.xy-0.5)*4.0;
    if(iResolution.x < iResolution.y)
    {
        uv.x *= iResolution.x/iResolution.y;
    }
    else
    {
        uv.y *= iResolution.y/iResolution.x;
    }

    // --- Kaleidoscope ---
    uv = mix( uv, Kaleidoscope( uv, NUM_SIDES, LOOP_TIME*1.0 ), USE_KALEIDOSCOPE ); 
    
    vec3 final_color = vec3( 0.0 );
    float final_density = 0.0;
    for ( int i = 0; i < 64; i++ ) {
        vec4 noise  = texture( iChannel0, vec2( float( i ) + 0.5, 0.5 ) / 256.0 );
        vec4 noise2 = texture( iChannel0, vec2( float( i ) + 0.5, 9.5 ) / 256.0 );
        
        // velocity
        vec2 vel = noise.xy * 2.0 - vec2( 1.0 );
        
        // center
        vec2 pos = noise.xy;
        pos += sin(LOOP_TIME) * vel * 0.2;
        pos = mix( fract( pos ), 1.0 - fract( pos ), mod( floor( pos ), 2.0 ) );
        
        // remap to screen
        pos = ( pos * 2.0 - 1.0 ) * 2.0;
        
        // radius
        float radius = clamp( noise.w, 0.3, 1.2 );
        radius *= radius * 0.4;
        
        // color
        vec3 color = noise2.xyz;
        
        // density
        float density = field( uv, pos, radius )*iForce/5.5;

        // accumulate
        final_density += density;       
        final_color += density * color;
    }

    final_density = clamp( final_density - 0.1, 0.0, 1.0 );

    
    final_density = pow( final_density, 3.0 );

    fragColor = vec4( final_color * final_density, 1.0 );
}
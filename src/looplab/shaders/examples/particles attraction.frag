
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================


float noise( vec2 co ) {
    return fract( sin( dot( co.xy, vec2( 12.9898, 78.233 ) ) ) * 43758.5453 );
}   
void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    
    float time = (LOOP_TIME+50.)*0.1;
    
    float u_brightness = pow(iForce/7.5, 3.0);
    float u_blobiness = 1.15;
    float u_particles = 1.1 + iComplexity *0.2;
    float u_limit = 1.0;
    float u_energy = 0.75 * 4.0;


    vec2 position = (fragCoord.xy / iResolution.xy-0.5)*.8;
    if(iResolution.x < iResolution.y)
    {
        position.x *= iResolution.x/iResolution.y;
    }
    else
    {
        position.y *= iResolution.y/iResolution.x;
    }

    float t = time * u_energy;

    float a = 0.0;
    float b = 0.0;
    float c = 0.0;

    vec2 pos;

    //float aspect = (iResolution.x / iResolution.y) ;

    vec2 center = vec2( 0., 0. );

    float na, nb, nc, nd, d;
    float limit = u_particles / u_limit;
    float step = 1.0 / u_particles;
    float n = 0.0;

    for ( float i = 0.0; i <=limit; i += 0.03 ) {

        vec2 np = vec2(n, 1-1);

        na = noise( np * 1.1 );
        nb = noise( np * 2.8 );
        nc = noise( np * 0.7 );
        nd = noise( np * 3.2 );

        pos = center;
        pos.x += sin(t*na) * cos(t*nb) * tan(t*na*0.15) * 0.4;
        pos.y += tan(t*nc) * sin(t*nd) * 0.4;

        d = pow( 1.6*na / length( pos - position ), u_blobiness );

        if ( i < limit * .333 ) a += d;
        else if ( i < limit * 2.9 ) b += d;
        else c += d;

        n += step;
        
    }
    
    vec3 col = vec3(pow(a*b* 0.0001, 4.))  * u_brightness;

    fragColor = vec4( col, 1. );
}

// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

// starDust - shadertoy intro
// Created by Dmitry Andreev - and'2014
// License Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.

#define iBaseHueRad 3.8

#define SPEED           (1.7)
#define WARMUP_TIME     (0.0)

// Shadertoy's sound is a bit out of sync every time you run it :(
#define SOUND_OFFSET    (-0.0)

float saturate(float x)
{
    return clamp(x, 0.0, 1.0);
}

float isectPlane(vec3 n, float d, vec3 org, vec3 dir)
{
    float t = -(dot(org, n) + d) / dot(dir, n);

    return t;
}


vec3 drawEffect(vec2 coord, float time)
{
    vec3 clr = vec3(0.0);
    const float far_dist = 10000.0;

    float mtime = 0. + time*2.0 / SPEED;
    vec2 uv = coord.xy / iResolution.xy;

    vec3 org = vec3(0.0);
    vec3 dir = vec3(uv.xy * 2.0 - 1.0, 1.0);

    // Animate tilt
    float ang = sin(time*1.0) * 0.3;
    vec3 odir = dir;
    dir.x = cos(ang) * odir.x + sin(ang) * odir.y;
    dir.y = sin(ang) * odir.x - cos(ang) * odir.y;

    // Animate FOV and aspect ratio
    dir.x *= 1.5 + 0.5 * sin(time*2.0 * 0.125);
    dir.y *= 1.5 + 0.5 * cos(time*2.0 * 0.25 + 0.5);

    // Animate view direction
    dir.x += 0.25 * sin(time*1.0);
    dir.y += 0.25 * sin(time*2.0);

    // Bend it like this
    dir.xy = mix(vec2(dir.x + 0.2 * cos(dir.y) - 0.1, dir.y), dir.xy,
        smoothstep(0.0, 1.0, saturate(0.5 * abs(mtime - 20.0))));

    // Bend it like that
    dir.xy = mix(vec2(dir.x + 0.1 * sin(4.0 * (dir.x + time)), dir.y), dir.xy,
        smoothstep(0.0, 1.0, saturate(0.5 * abs(mtime - 28.0))));

    // Cycle between long blurry and short sharp particles
    vec2 param = mix(vec2(60.0, 0.8), vec2(800.0, 3.0),
        pow(0.5 + 0.5 * sin(time*1.0), 2.0));

    float lt = fract(mtime / 2.0) * 4.0;
    vec2 mutes = vec2(0.0);
    
   
    float power = pow(iForce/5.5, 3.);
    for (int k = 0; k < 2; k++)
    for (int i = 0; i < (iComplexity-1)*15+5; i++)
    {
        vec3 pn = vec3(k > 0 ? -1.0 : 1.0, 0.0, 0.0);
        float t = isectPlane(pn, 100.0 + float(i) * 20.0/power, org, dir);

        if (t <= 0.0 || t >= far_dist) continue;

        vec3 p = org + dir * t;
        vec3 vdir = normalize(-p);

        // Create particle lanes by quantizing position
        vec3 pp = ceil(p / 100.0) * 100.0;

        // Pseudo-random variables
        float n = pp.y + float(i) + float(k) * 123.0;
        float q = fract(sin(n * 123.456) * 234.345);
        float q2= fract(sin(n * 234.123) * 345.234);

        q = sin(p.z * 0.0003 + 1.0*time * (0.25 + 0.75 * q2) + q * 12.0);

        // Smooth particle edges out
        q = saturate(q * param.x - param.x + 1.0) * param.y;
        q *= saturate(4.0 - 8.0 * abs(-50.0 + pp.y - p.y) / 100.0);

        // Fade out based on distance
        q *= 1.0 - saturate(pow(t / far_dist, 5.0));

        // Fade out based on view angle
        float fn = 1.0 - pow(1.0 - dot(vdir, pn), 2.0);
        q *= 2.0 * smoothstep(0.0, 1.0, fn);

        // Flash fade left or right plane
        q *= 1.0 - 0.9 * (k == 0 ? mutes.x : mutes.y);

        // Cycle palettes
        const vec3 orange = vec3(1.0, 0.7, 0.4);
        const vec3 blue   = vec3(0.4, 0.7, 1.0);
        clr += q * mix(orange, blue, 0.5 + 0.5 * sin(time + q2));

       
    }

    clr *= 0.4;

    // Cycle gammas
    clr.r = pow(clr.r, 0.75 + 0.35 * sin(time ));
    clr.b = pow(clr.b, 0.75 - 0.35 * sin(time ));   

  
    // Vignette in linear space (looks better)
    clr *= clr;
    clr *= 1.4 ;
    clr *= 1.0 - 1.5 * dot(uv - 0.5, uv - 0.5);
    clr = sqrt(max(vec3(0.0), clr));

    return clr;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    float time = max(0.0, LOOP_TIME*1.0);    
    vec3 clr = drawEffect(fragCoord.xy, time);    

    fragColor = vec4(clr, 1.0);
}
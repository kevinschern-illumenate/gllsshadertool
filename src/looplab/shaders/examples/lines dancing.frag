
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

#define StepSize 0.35
float LineCount = iComplexity * 2.;

//Function to draw a line, taken from the watch shader
float line(vec2 p, vec2 a, vec2 b, float thickness )
{
    vec2 pa = p - a;
    vec2 ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return 1.0 - smoothstep(thickness * 0.8, thickness * 1.2, length(pa - ba * h));
}   

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = (fragCoord.xy / iResolution.xy) * 2.0 - 1.0;

    // convert the input coordinates by a cosinus
    // warpMultiplier is the frequency
    float warpMultiplier = (3.0 + 2.5 * sin(LOOP_TIME*1.0));
    vec2 warped = sin(uv * 6.28318530718 * warpMultiplier);

    // blend between the warpeffect and no effect
    // don't go all the way to the warp effect
    float warpornot = smoothstep(-0.5, 1.3, -0.2-0.3*abs(sin((LOOP_TIME+3.1416) * 0.23)));
    uv = mix(uv, warped, warpornot);

    //float warpornot = 1.;
    // Variate the thickness of the lines
    float thickness = 0.1 * pow(iForce / 5.5, 2.5);
    //thickness *= 1.0 + (warpMultiplier * warpornot);
    float gt = LOOP_TIME*2.0;

    // Add 10 lines to the pixel
    vec4 color = vec4(0.0, 0.0, 0.0, 1.0);
    for (int i = 0; i < LineCount; i++)
    {
        gt += StepSize;

        //Calculate the next two points
        vec2 point1 = vec2(sin(gt * 0.39), cos(gt * 0.63));
        vec2 point2 = vec2(cos(gt * 0.69), sin(gt * 0.29));

        // Fade older lines
        color.rgb = 0.95 * color.rgb;

        // Add new line
        color.rgb += line(  uv,
                            point1, point2,
                            thickness       )
                    //With color
                    * ( 0.3 +
                        0.3 * vec3( sin(gt * 3.13),
                                    sin(gt * 1.69),
                                    sin(gt * 2.67)));
}

    // Clamp oversaturation
    fragColor = clamp(color, 0.0, 1.0);
}
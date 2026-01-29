
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

const float overallSpeed = 0.35;
float power = pow(iForce/5.5, 3.);
float gridSmoothWidth = 0.115*power;
const float axisWidth = 0.05;
const float majorLineWidth = 1.125;
const float minorLineWidth = 0.125;
const float majorLineFrequency = 5.0;
const float minorLineFrequency = 1.0;
const vec4 gridColor = vec4(1.);
const float scale = 7.0;
const vec4 lineColor = vec4(0.8);
const float minLineWidth = 0.02;
const float maxLineWidth = 0.5;
const float lineSpeed = 1.0 * overallSpeed;
const float lineAmplitude = 1.0;
const float lineFrequency = 0.1;
const float warpSpeed = 0.3 * overallSpeed;
const float warpFrequency = 0.5;
const float warpAmplitude = 2.0;
const float offsetFrequency = 0.5;
const float offsetSpeed = 1.33 * overallSpeed;
const float minOffsetSpread = 0.3;
const float maxOffsetSpread = 5.0;
float linesPerGroup = pow(0.+iComplexity,2.)+1.;

const vec4[] bgColors = vec4[]
    (
        lineColor * 0.5,
        lineColor - vec4(0.2, 0.2, 0.7, 1)
        );

#define drawCircle(pos, radius, coord) smoothstep(radius + gridSmoothWidth, radius, length(coord - (pos)))

#define drawSmoothLine(pos, halfWidth, t) smoothstep(halfWidth, 0.0, abs(pos - (t)))

#define drawCrispLine(pos, halfWidth, t) smoothstep(halfWidth + gridSmoothWidth, halfWidth, abs(pos - (t)))

#define drawPeriodicLine(freq, width, t) drawCrispLine(freq / 2.0, width, abs(mod(t, freq) - (freq) / 2.0))

float drawGridLines(float axis)   
{
    return   drawCrispLine(0.0, axisWidth, axis)
           + drawPeriodicLine(majorLineFrequency, majorLineWidth, axis)
           + drawPeriodicLine(minorLineFrequency, minorLineWidth, axis);
}

float drawGrid(vec2 space)
{
    return min(1., drawGridLines(space.x)
                  +drawGridLines(space.y));
}

// probably can optimize w/ noise, but currently using fourier transform
float random(float t)
{
    return (cos(t) + cos(t * 1.3 + 1.3) + cos(t * 1.4 + 1.4)) / 3.0;   
}

float getPlasmaY(float x, float horizontalFade, float offset)   
{
    return random(x * lineFrequency + LOOP_TIME * lineSpeed) * horizontalFade * lineAmplitude + offset;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord.xy / iResolution.xy;
    

    vec2 space = (fragCoord.xy / iResolution.xy-0.5)*scale*1.5;
    if(iResolution.x < iResolution.y)
    {
        space.x *= iResolution.x/iResolution.y;
    }
    else
    {
        space.y *= iResolution.y/iResolution.x;
    }
    
    float horizontalFade = 1.0 - (cos(uv.x * 6.28) * 0.5 + 0.5);
    float verticalFade = 1.0 - (cos(uv.y * 6.28) * 0.5 + 0.5);

    // fun with nonlinear transformations! (wind / turbulence)
    space.y += random(space.x * warpFrequency + sin(LOOP_TIME) * warpSpeed) * warpAmplitude * (0.5 + horizontalFade);
    space.x += random(space.y * warpFrequency + sin(LOOP_TIME) * warpSpeed + 2.0) * warpAmplitude * horizontalFade;
    
    vec4 lines = vec4(0);
    
    for(int l = 0; l < linesPerGroup; l++)
    {
        float normalizedLineIndex = float(l) / float(linesPerGroup);
        float offsetTime = LOOP_TIME * offsetSpeed;
        float offsetPosition = float(l) + space.x * offsetFrequency;
        float rand = random(offsetPosition + offsetTime) * 0.5 + 0.5;
        float halfWidth = mix(minLineWidth, maxLineWidth, rand * horizontalFade) / 2.0;
        float offset = random(offsetPosition + offsetTime * (1.0 + normalizedLineIndex)) * mix(minOffsetSpread, maxOffsetSpread, horizontalFade);
        float linePosition = getPlasmaY(space.x, horizontalFade, offset);
        float line = drawSmoothLine(linePosition, halfWidth, space.y) / 2.0 + drawCrispLine(linePosition, halfWidth * 0.15, space.y);
        
        float circleX = mod(float(l) + LOOP_TIME * lineSpeed, 25.0) - 12.0;
        vec2 circlePosition = vec2(circleX, getPlasmaY(circleX, horizontalFade, offset));
        float circle = drawCircle(circlePosition, 0.01, space) * 4.0;
        
        
        line = line + circle;
        lines += line * lineColor * rand;
    }
    
    //fragColor = mix(bgColors[0], bgColors[1], uv.x);
    fragColor *= verticalFade;
    fragColor.a = 1.0;
    // debug grid:
    //fragColor = mix(fragColor, gridColor, drawGrid(space));
    fragColor += lines;
}
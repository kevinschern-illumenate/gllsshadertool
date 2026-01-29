// ----------------------------------------------------
//  "Singing Wisps" by Krzysztof Kondrak @k_kondrak
// ----------------------------------------------------

#define iBaseHueRad 4.19

void mainImage( out vec4 o, in vec2 p )
{
    float d = (.5 - distance(p.y, iResolution.y * .5) / iResolution.y);
    float c = 3. * d * texture(iAudioFFT, vec2(p.x * .15 * (iNbItems / 32.0) / iResolution.x, 0.)).r * pow(iForce/5.5,2.0);
    o = c * vec4(.85, .85, 2., 1.);
}
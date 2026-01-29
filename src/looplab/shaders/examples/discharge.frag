// Created by Alex Kluchikov


// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

#define iBaseHueRad 4.55172

#define float3 vec3
#define float2 vec2
#define float4 vec4

float3 MIX(float3 x, float3 y)
{
	return abs(x-y);
}    

float CV(float3 c, float2 uv)
{
    float size=640./iResolution.x*0.003;
    float l=clamp(size*(length(c.xy-uv)-c.z),0.,1.);
	return 1.-l;
}

void mainImage(out float4 O, in float2 I)
{
    O=float4(0,0,0,1);
    for(float i=0.;i<iComplexity * 200.;i+=13.)
    {
        
        float3 c=float3(1.0,1.0,1.0);
		O.rgb=MIX(O.rgb,c*CV(float3(
			iResolution.x*(1.+sin(LOOP_TIME*1.0+(i-1400.)*1.35))*.5,
			iResolution.y*(1.+sin(LOOP_TIME*1.0+(i-1200.)*1.61))*.5,
			0.0),I));
    }
	
	float power = iForce / 30.0 + 1.0;
	float trail = (11.0 - iForce2) / 11.0;
	
    O.rgb=(1.-O.rgb)*power;
    O.rgb=pow(O.rgb,trail*float3(42.,32.,12.));
}
// The Universe Within - by Martijn Steinrucken aka BigWings 2018
// Email:countfrolic@gmail.com Twitter:@The_ArtOfCode
// License Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.

// After listening to an interview with Michael Pollan on the Joe Rogan
// podcast I got interested in mystic experiences that people seem to
// have when using certain psycoactive substances. 
//
// For best results, watch fullscreen, with music, in a dark room.
// 
// I had an unused 'blockchain effect' lying around and used it as
// a base for this effect. Uncomment the SIMPLE define to see where
// this came from.
// 
// Use the mouse to get some 3d parallax.

// Music - Terrence McKenna Mashup - Jason Burruss Remixes
// https://soundcloud.com/jason-burruss-remixes/terrence-mckenna-mashup
//
// YouTube video of this effect:
// https://youtu.be/GAhu4ngQa48
//
// YouTube Tutorial for this effect:
// https://youtu.be/3CycKKJiwis
// https://www.shadertoy.com/view/lscczl

#define S(a, b, t) smoothstep(a, b, t)
#define NUM_LAYERS (iComplexity+0.0)

//#define SIMPLE


float N21(vec2 p)
{	// Dave Hoskins - https://www.shadertoy.com/view/4djSRW
	vec3 p3  = fract(vec3(p.xyx) * vec3(443.897, 441.423, 437.195));
    p3 += dot(p3, p3.yzx + 19.19);
    return fract((p3.x + p3.y) * p3.z);
}

vec2 GetPos(vec2 id, vec2 offs, float t) {
    float n = N21(id+offs);
    float n1 = fract(n*10.);
    float n2 = fract(n*100.);
    float a = t+n;
    return offs + vec2(sin(a*n1), cos(a*n2))*.4;
}

float GetT(vec2 ro, vec2 rd, vec2 p) {
	return dot(p-ro, rd); 
}

float LineDist(vec3 a, vec3 b, vec3 p) {
	return length(cross(b-a, p-a))/length(p-a);
}

float df_line( in vec2 a, in vec2 b, in vec2 p)
{
    vec2 pa = p - a, ba = b - a;
	float h = clamp(dot(pa,ba) / dot(ba,ba), 0., 1.);	
	return length(pa - ba * h);
}

float line(vec2 a, vec2 b, vec2 uv) {
    float r1 = .04;
    float r2 = .01;
    
    float d = df_line(a, b, uv);
    float d2 = length(a-b);
    float fade = S(1.5, .5, d2);
    
    fade += S(.05, .02, abs(d2-.75));
    return S(r1, r2, d)*fade*0.05;
}
float power = pow(iForce/10.0+0.8, 1.);
float NetLayer(vec2 st, float n, float t) {
    vec2 id = floor(st)+n;

    st = fract(st)-.5;
   
    vec2 p[9];
    int i=0;
    for(float y=-1.; y<=1.; y++) {
    	for(float x=-1.; x<=1.; x++) {
            p[i++] = GetPos(id, vec2(x,y), t);
    	}
    }
    
    float m = 0.;
    float sparkle = 0.;
    
    for(int i=0; i<9; i++) {
        m += line(p[4], p[i], st);
		float fft  = texture( iAudioFFT, vec2((p[i].x+p[i].y)*0.5,0.25) ).x*power;
        float d = length(st-p[i]);

        float s = (.09/(d*d));
        s *= S(10., .7, d);
        float pulse = sin((fract(p[i].x)+fract(p[i].y)+t)*5.)*.4+.6;
        pulse = pow(fft*1., 10.);

        s *= pulse;
        sparkle += s;
    }
    
    m += line(p[1], p[3], st);
	m += line(p[1], p[5], st);
    m += line(p[7], p[5], st);
    m += line(p[7], p[3], st);
    
    float sPhase = 1.;//(sin(t+n)+sin(t*.1))*.25+.5;
    //sPhase += pow(sin(t*.1)*.5+.5, 50.)*5.;
    m += sparkle;//(*.5+.5);
    
    return min(m*2.0, 5.);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = (fragCoord-iResolution.xy*.5)/iResolution.y;
	vec2 M = iMouse.xy/iResolution.xy-.5;
    
    float t = iComplexity > 1 ? iTime * 0.1+10. : 0.;
    
    float s = sin(t);
    float c = cos(t);
    mat2 rot = mat2(c, -s, s, c);
    vec2 st = uv*rot;  
	M *= rot*2.;
    
    float m = 0.;
    for(float i=0.; i<1.; i+=1./NUM_LAYERS) {
        float z = fract(t+i);
        float size = mix(15., 1., z);
        float fade = iComplexity > 1 ? S(0., .6, z)*S(1., .8, z) : 1.;
        
        m += fade * NetLayer(st*size-M*z, i, iTime+10.);
    }
    
	float fft  = 0.;
    float glow = -uv.y*fft*2.;
   	float colOffset = (iAudioLow*3.0 + 2.0*iAudioMid + iAudioHi);
    vec3 baseCol = vec3(s, cos(5.*colOffset), -sin(10.*colOffset))*.4+.6;
    vec3 col = baseCol*m;
    col += baseCol*glow;
    
    #ifdef SIMPLE
    uv *= 10.;
    col = vec3(1);
    uv = fract(uv);
    //if(uv.x>.98 || uv.y>.98) col += 1.;
    #else
    col *= 1.-dot(uv,uv);
    //t = iTime;
    //col *= ;
    #endif
    
    fragColor = vec4(col,1);
}
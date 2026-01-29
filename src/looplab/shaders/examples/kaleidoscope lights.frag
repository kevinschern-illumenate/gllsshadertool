

// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================

#define KALEIDO 1
float LIGHTCOUNT = iComplexity * 20.;
float power = pow(iForce/5., 3.);

#define v2Resolution iResolution
#define out_color fragColor
#define time (LOOP_TIME*1.0)

#define pi 3.141592


vec2 r2(vec2 uv) {
  return fract(sin(uv*vec2(1236.512,2975.233)+uv.yx*vec2(4327.135,6439.123)+vec2(1234.93,1347.367))*vec2(4213.523744,974.93242));
}

vec2 r2(int i) {
  return fract(sin(float(i)*vec2(1236.512,2975.233)+vec2(1234.93,1347.367))*vec2(4213.523744,974.93242));
}

mat2 rot(float a) {
  float ca=cos(a);
  float sa=sin(a);
  return mat2(ca,sa,-sa,ca);
}

vec2 mir(vec2 uv, float a) {

  mat2 ra=rot(a);
  uv *= ra;
  uv.y=abs(uv.y);
  uv *= ra;

  return uv;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
  vec2 uv = (fragCoord.xy / iResolution.xy-0.5);
    if(iResolution.x < iResolution.y)
    {
        uv.x *= iResolution.x/iResolution.y;
    }
    else
    {
        uv.y *= iResolution.y/iResolution.x;
    }
    uv*= 0.5;

  float mt=time*1.0;
#if KALEIDO
  uv = mir(uv, mt*0.2);
  uv = mir(uv, -mt*0.4);
  uv = mir(uv, mt*0.6);
  uv = mir(uv, -mt*0.9);
#endif

  float ht=time*1.0;
  uv += abs(vec2(sin(ht),cos(ht)))*(sin(time*1.0)*0.5+0.5)*0.3;

  vec3 tcol=mix(vec3(0.8,0.2,0.2),vec3(0.2,0.8,0.9),sin(1234.12134+time*vec3(0.5,1.3,2.8)));
  float pt=time*1.0;
  float pulse = abs(fract(pt*floor(abs(fract(pt*4.0)*4.0-0.5)*2.0))-0.5)*2.0;

  float st=time*1.0;

  float d=10000.0;
  vec3 col = vec3(0);
  for(int i=0; i<LIGHTCOUNT; ++i) {

    vec2 rr=r2(i*10);
    float a=rr.x*pi*2.0 + st + sin(st*0.6+rr.y)*1.3 + sin(st*0.2+rr.y)*0.9;
    vec2 p = uv+(r2(i)-0.5)*0.5 + vec2(cos(a),sin(a))*0.2;
    float lp=length(p);
    d=min(d,lp-0.01);

    vec3 lcol=mix(vec3(0.8,0.2,0.2),vec3(0.2,0.8,0.9),sin(rr.y*100.0*vec3(0.5,1.3,2.8)));
    lcol = mix(lcol,tcol,pulse);
    float bd = 0.0015/lp*power;
    col += lcol*bd;

  }

  //col = vec3(0.003)/max(0.001,d);
  float gt=time*1.0;
  vec3 lcol=mix(vec3(0.8,0.2,0.2),vec3(0.2,0.8,0.9),sin(time*vec3(0.5,1.3,2.8)));
  col += abs(fract(gt*floor(abs(fract(gt*4.0)*4.0)-0.5)*2.0)-0.5)*2.0*lcol*pow(abs(fract(d*30.0-time*1.0)-0.5)*2.0,8.0)*max(0.0,0.6 / length(uv)-0.9);

  out_color = vec4(col,0);
}
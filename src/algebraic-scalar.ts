/** Exact positive prime monomials for the source scalar/root-extension carrier. */
import {createNativeExecutor} from './native-operators.js';
import {rational,type Rational} from './law.js';

export interface PrimePower {prime:string; exponent:Rational}
export interface AlgebraicScalar {powers:PrimePower[]}
const MAX_PRIME=1_000_000;
function q(x:Rational):Rational {
  if(!x || typeof x.numerator!=='string' || typeof x.denominator!=='string' || x.numerator.length>128 || x.denominator.length>128)throw new TypeError('exponents require bounded exact integer strings');
  return rational(x.numerator,x.denominator);
}
function sum(a:Rational,b:Rational):Rational{return rational(BigInt(a.numerator)*BigInt(b.denominator)+BigInt(b.numerator)*BigInt(a.denominator),BigInt(a.denominator)*BigInt(b.denominator));}
function times(a:Rational,b:Rational):Rational{return rational(BigInt(a.numerator)*BigInt(b.numerator),BigInt(a.denominator)*BigInt(b.denominator));}
function prime(s:string):number {
  if(typeof s!=='string' || !/^[1-9][0-9]{0,6}$/.test(s))throw new TypeError('prime must be a bounded integer string');
  const p=Number(s);if(p<2 || p>MAX_PRIME)throw new RangeError('supported primes lie between2and1000000');
  for(let d=2;d*d<=p;d++)if(p%d===0)throw new TypeError('monomial bases must be prime');return p;
}
function floor(x:Rational):bigint {const n=BigInt(x.numerator),d=BigInt(x.denominator);return n>=0n?n/d:-((-n+d-1n)/d);}
function mod(n:bigint,d:bigint):bigint{return ((n%d)+d)%d;}
function normal(value:AlgebraicScalar):AlgebraicScalar {
  if(!value || !Array.isArray(value.powers) || value.powers.length>64)throw new TypeError('at most64prime-power entries are supported');
  const exponents=new Map<string,Rational>();
  for(const term of value.powers){prime(term.prime);const e=q(term.exponent);exponents.set(term.prime,q(sum(exponents.get(term.prime)??rational(0,1),e)));}
  return {powers:[...exponents].filter(([,e])=>e.numerator!=='0').sort(([a],[b])=>Number(a)-Number(b)).map(([p,e])=>({prime:p,exponent:e}))};
}
function exp(value:AlgebraicScalar,p:string):Rational{return value.powers.find(x=>x.prime===p)?.exponent??rational(0,1);}

/** Source hash is checked before this exact extension can be bound to a native registry. */
export function createAlgebraicScalar(raw:string|Uint8Array,sourceId:string){
  const binding=createNativeExecutor(raw,sourceId).registry().find(x=>x.id==='MEC-01')!.source;
  const make=(powers:PrimePower[]):AlgebraicScalar=>normal({powers});
  const multiply=(a:AlgebraicScalar,b:AlgebraicScalar):AlgebraicScalar=>make([...normal(a).powers,...normal(b).powers]);
  const power=(a:AlgebraicScalar,p:Rational):AlgebraicScalar=>{const exponent=q(p);return make(normal(a).powers.map(t=>({prime:t.prime,exponent:times(t.exponent,exponent)})));};
  const inverse=(a:AlgebraicScalar):AlgebraicScalar=>power(a,rational(-1,1));
  const divide=(a:AlgebraicScalar,b:AlgebraicScalar):AlgebraicScalar=>multiply(a,inverse(b));
  const equal=(a:AlgebraicScalar,b:AlgebraicScalar):boolean=>JSON.stringify(normal(a))===JSON.stringify(normal(b));
  const fromRational=(value:Rational):AlgebraicScalar=>{
    const v=q(value),n=BigInt(v.numerator),d=BigInt(v.denominator);
    if(n<=0n)throw new RangeError('positive scalar required');
    if(n>1_000_000_000_000n || d>1_000_000_000_000n)throw new RangeError('rational factorization input exceeds10^12');
    const terms:PrimePower[]=[];
    const factor=(initial:bigint,sign:bigint)=>{let left=initial;for(let p=2n;p*p<=left;p++){let count=0n;while(left%p===0n){left/=p;count++;}if(count)terms.push({prime:p.toString(),exponent:rational(sign*count,1)});}if(left>1n)terms.push({prime:left.toString(),exponent:rational(sign,1)});};
    factor(n,1n);factor(d,-1n);return make(terms);
  };
  const asRational=(value:AlgebraicScalar):{status:'rational';value:Rational}|{status:'non-rational'|'out-of-scope';reason:string}=>{
    const v=normal(value);if(v.powers.some(t=>t.exponent.denominator!=='1'))return {status:'non-rational',reason:'A noninteger prime exponent cannot equal a positive rational; clearing denominators and unique prime factorization separate it.'};
    let budget=0n;for(const t of v.powers){const e=BigInt(t.exponent.numerator);budget+=(e<0n?-e:e)*BigInt(Number(t.prime).toString(2).length);}
    if(budget>32768n)return {status:'out-of-scope',reason:'Exact integer output exceeds the32768bit materialization budget; the monomial remains exact.'};
    let numerator=1n,denominator=1n;for(const t of v.powers){const e=BigInt(t.exponent.numerator);if(e>=0n)numerator*=BigInt(t.prime)**e;else denominator*=BigInt(t.prime)**(-e);}
    return {status:'rational',value:rational(numerator,denominator)};
  };
  const moduloOctaves=(value:AlgebraicScalar):{representative:AlgebraicScalar;removedOctaves:string}=>{
    const v=normal(value),octaves=floor(exp(v,'2'));
    return {representative:multiply(v,make([{prime:'2',exponent:rational(-octaves,1)}])),removedOctaves:octaves.toString()};
  };
  const inG=(value:AlgebraicScalar):boolean=>normal(value).powers.every(t=>(t.prime==='2'||t.prime==='3')&&t.exponent.denominator==='1');
  const inH=(value:AlgebraicScalar):boolean=>normal(value).powers.every(t=>t.prime==='3'?t.exponent.denominator==='1':t.prime==='2'?(12n*BigInt(t.exponent.numerator))%BigInt(t.exponent.denominator)===0n:false);
  const hCoordinates=(value:AlgebraicScalar)=>{
    const v=normal(value);if(!inH(v))return {status:'outside-source-H' as const,reason:'H only has prime2exponents in(1/12)Z and integer prime3exponents.'};
    const e2=exp(v,'2'),e3=exp(v,'3'),rootStep=Number(mod(12n*BigInt(e2.numerator)/BigInt(e2.denominator),12n));
    return {status:'represented' as const,rootStepMod12:rootStep,prime3Exponent:e3.numerator,quotientByG:{cyclicOrder:12,rootStepMod12:rootStep},quotientByIntegerOctaves:{cyclicOrder:12,rootStepMod12:rootStep,prime3Exponent:e3.numerator,infiniteCoordinateRetained:true}};
  };
  return {source:binding,scope:{carrier:'positive finite prime monomials with rational exponents',primeMax:MAX_PRIME,termMax:64,exponentIntegerStringMaxDigits:128,rationalFactorizationInputMax:'1000000000000',rationalMaterializationBitBudget:32768,octaveSection:'prime2exponent in[0,1); an algebraic representative, not frequency normalized into[1,2)',exclusions:['sums of radicals','arbitrary algebraic numbers','complex roots','ordering/approximate frequency evaluation','canonical historical orientation']},make,multiply,power,inverse,divide,equal,fromRational,asRational,moduloOctaves,inG,inH,hCoordinates};
}

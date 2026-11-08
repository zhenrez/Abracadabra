/** Exact conditional contact timing. This is an interval adapter, not a genealogy ontology. */
import {rational, type Rational} from './law.js';

export interface EventWindow {
  lower: Rational | null;
  upper: Rational | null;
  lowerClosed: boolean;
  upperClosed: boolean;
}
export interface ContactResult {
  feasible: boolean;
  admissibleContact: EventWindow | null;
  witness: {donorOnset: Rational; contact: Rational; recipientOnset: Rational} | null;
  reason: string;
}

function normal(x: Rational): Rational {
  if (!x || typeof x.numerator!=='string' || typeof x.denominator!=='string') throw new TypeError('exact integer strings required');
  return rational(x.numerator,x.denominator);
}
function cmp(a: Rational,b: Rational): number {
  const x=BigInt(a.numerator)*BigInt(b.denominator)-BigInt(b.numerator)*BigInt(a.denominator);
  return x<0n?-1:x>0n?1:0;
}
function plus(a: Rational,b: Rational): Rational {
  return rational(BigInt(a.numerator)*BigInt(b.denominator)+BigInt(b.numerator)*BigInt(a.denominator),
    BigInt(a.denominator)*BigInt(b.denominator));
}
function window(x: EventWindow): EventWindow {
  if (!x || typeof x.lowerClosed!=='boolean' || typeof x.upperClosed!=='boolean') throw new TypeError('endpoint inclusion flags required');
  return {lower:x.lower===null?null:normal(x.lower),upper:x.upper===null?null:normal(x.upper),
    lowerClosed:x.lower!==null&&x.lowerClosed,upperClosed:x.upper!==null&&x.upperClosed};
}
function inputWindow(x: EventWindow): EventWindow {
  const value=window(x);
  for(const endpoint of [value.lower,value.upper])if(endpoint!==null
      &&(endpoint.numerator.length>128||endpoint.denominator.length>128))throw new RangeError('input endpoints exceed128integer-string digits');
  return value;
}
export function windowEmpty(value: EventWindow): boolean {
  const x=window(value);
  if (x.lower===null || x.upper===null) return false;
  const c=cmp(x.lower,x.upper);
  return c>0 || (c===0 && !(x.lowerClosed&&x.upperClosed));
}
export function intersectWindows(...values: EventWindow[]): EventWindow {
  let result: EventWindow={lower:null,upper:null,lowerClosed:false,upperClosed:false};
  for (const input of values) {
    const x=window(input);
    if(x.lower!==null){
      const c=result.lower===null?1:cmp(x.lower,result.lower);
      if(c>0){result.lower=x.lower;result.lowerClosed=x.lowerClosed;}
      else if(c===0)result.lowerClosed=result.lowerClosed&&x.lowerClosed;
    }
    if(x.upper!==null){
      const c=result.upper===null?-1:cmp(x.upper,result.upper);
      if(c<0){result.upper=x.upper;result.upperClosed=x.upperClosed;}
      else if(c===0)result.upperClosed=result.upperClosed&&x.upperClosed;
    }
  }
  return result;
}
function choose(x: EventWindow): Rational {
  if(windowEmpty(x))throw new RangeError('cannot select from an empty interval');
  if(x.lower!==null&&x.upper!==null){
    if(cmp(x.lower,x.upper)===0)return x.lower;
    const total=plus(x.lower,x.upper);
    return rational(total.numerator,BigInt(total.denominator)*2n);
  }
  if(x.lower!==null)return plus(x.lower,rational(1,1));
  if(x.upper!==null)return plus(x.upper,rational(-1,1));
  return rational(0,1);
}
export function windowContains(input: EventWindow,value: Rational): boolean {
  const x=window(input),v=normal(value);
  return !windowEmpty(x) && (x.lower===null || cmp(v,x.lower)>0 || (cmp(v,x.lower)===0&&x.lowerClosed))
    && (x.upper===null || cmp(v,x.upper)<0 || (cmp(v,x.upper)===0&&x.upperClosed));
}

/** Solve d<k<=r over real intervals; strictDonor=false explicitly allows d=k. */
export function contactTiming(donor: EventWindow,contact: EventWindow,recipient: EventWindow,strictDonor=true): ContactResult {
  if(typeof strictDonor!=='boolean')throw new TypeError('strictDonor must be explicit boolean');
  // The resource bound applies to supplied endpoints, never to exact derived witnesses.
  const d=inputWindow(donor),k=inputWindow(contact),r=inputWindow(recipient);
  if([d,k,r].some(windowEmpty))return {feasible:false,admissibleContact:null,witness:null,reason:'An input event window is empty.'};
  const admissible=intersectWindows(k,{lower:d.lower,lowerClosed:!strictDonor&&d.lowerClosed,
    upper:r.upper,upperClosed:r.upperClosed});
  if(windowEmpty(admissible))return {feasible:false,admissibleContact:admissible,witness:null,
    reason:'No contact time is after an available donor onset and no later than an available recipient acquisition.'};
  const at=choose(admissible);
  const dw=intersectWindows(d,{lower:null,lowerClosed:false,upper:at,upperClosed:!strictDonor});
  const rw=intersectWindows(r,{lower:at,lowerClosed:true,upper:null,upperClosed:false});
  const witness={donorOnset:choose(dw),contact:at,recipientOnset:choose(rw)};
  if(!windowContains(d,witness.donorOnset)||!windowContains(k,at)||!windowContains(r,witness.recipientOnset)
      ||(strictDonor?cmp(witness.donorOnset,at)>=0:cmp(witness.donorOnset,at)>0)||cmp(at,witness.recipientOnset)>0)
    throw new Error('internal exact-witness verification failed');
  return {feasible:true,admissibleContact:admissible,witness,
    reason:'A real-valued timing assignment exists within the declared intervals; historical transmission is not established.'};
}

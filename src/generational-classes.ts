/** Recovered five-direction construction. Its mathematical depth is frame-qualified. */
export interface CompositionAddress { frame: string; generation: number; counts: number[] }
const safe=(n:number,name:string)=>{if(!Number.isSafeInteger(n)||n<0)throw new TypeError(name+' must be a nonnegative safe integer');return n;};
export function binomial(n:bigint,k:number):bigint{
 safe(k,'k');if(n<0n)throw new TypeError('n must be nonnegative');
 if(BigInt(k)>n)return 0n;if(k>1000)throw new RangeError('Explicit calculation budget: at most1000factors');
 let out=1n;for(let i=1;i<=k;i++)out=out*(n-BigInt(k-i))/BigInt(i);return out;
}
export function compositionCount(generators:number,depth:number):bigint{
 safe(generators,'generators');safe(depth,'depth');if(!generators)throw new TypeError('At least one generator required');
 return binomial(BigInt(depth)+BigInt(generators)-1n,generators-1);
}
export function compositions(generators:number,depth:number,budget=50000):number[][]{
 safe(budget,'budget');const total=compositionCount(generators,depth);
 if(total>BigInt(budget))throw new RangeError('Enumeration exceeds declared display budget; exact count remains available');
 const result:number[][]=[];
 const step=(left:number,slots:number,prefix:number[])=>{if(slots===1){result.push([...prefix,left]);return;}for(let v=0;v<=left;v++)step(left-v,slots-1,[...prefix,v]);};
 step(depth,generators,[]);return result;
}
export function constructionDepth(counts:readonly number[]):number{
 if(!counts.length)throw new TypeError('Nonempty address required');let out=0;
 for(const x of counts){out+=safe(x,'count');if(!Number.isSafeInteger(out))throw new RangeError('Address depth exceeds integer representation');}return out;
}
export function mathematicalPredecessors(counts:readonly number[]){constructionDepth(counts);return counts.flatMap((x,j)=>{if(!x)return[];const previous=[...counts];previous[j]!--;return[{generatorIndex:j,counts:previous,relationship:'alternative-last-step-history' as const}];});}
export function pentagonalEndpoint(counts:readonly number[]){
 const depth=constructionDepth(counts);if(counts.length!==5)throw new TypeError('This source uses five directions');
 const basis=counts.slice(0,4).map(x=>x-counts[4]!);
 const embedding=(power:number)=>[basis.reduce((v,x,j)=>v+x*Math.cos(2*Math.PI*power*j/5),0),basis.reduce((v,x,j)=>v+x*Math.sin(2*Math.PI*power*j/5),0)];
 return{depth,cyclotomicBasis:basis,zeroEndpoint:basis.every(x=>x===0),
   minkowskiR4:[...embedding(1),...embedding(2)],
   exactMeaning:'Coefficients in1,zeta5,zeta5^2,zeta5^3; zeta5^4=-1-zeta5-zeta5^2-zeta5^3. Floating R4 embeddings are display only.',
   acousticFrequency:null,universalSunnyGeneration:null};
}
export function rotatePentagonalAddress(counts:readonly number[]){pentagonalEndpoint(counts);return[counts[4]!,...counts.slice(0,4)];}
export function balancedInheritance(counts:readonly number[],blocks=1){
 safe(blocks,'blocks');const before=pentagonalEndpoint(counts),afterCounts=counts.map(x=>x+blocks),after=pentagonalEndpoint(afterCounts);
 return{before,after,counts:afterCounts,addedConstructionSteps:5*blocks,
  normalizedEndpointFactor:before.depth===0?null:{numerator:String(before.depth),denominator:String(after.depth)},
  observable:'normalized geometric endpoint; no automatic acoustic calibration'};
}

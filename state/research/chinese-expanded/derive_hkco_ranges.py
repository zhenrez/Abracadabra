"""Bounded source-coordinate transcription of first-party HKCO2025 ranges.
Leaves non-keyed diatonic winds and retunable zheng out of chromatic enumeration.
"""
from pathlib import Path
import hashlib,json,math
import pdfplumber
HERE=Path(__file__).resolve().parent
PDF=HERE/'hkco-range2025.pdf'
page=pdfplumber.open(PDF).pages[0]
music=[c for c in page.chars if 'Maestro' in c['fontname'] or 'EngraverFontSet' in c['fontname']]
heads=[c for c in music if c['text'] in ['w','œ']]
clefs=[c for c in music if c['text'] in ['&','?','B','V','\uf0a0','\uf0e6','t']]
hl=sorted([l for l in page.lines if abs(l['top']-l['bottom'])<.01 and abs(l['x0']-102.96)<.1 and l['x1']-l['x0']>50],key=lambda l:l['top'])
assert len(hl)==170
staffs=[hl[i:i+5] for i in range(0,170,5)]
def oy(c):return page.height-c['matrix'][5]
def head(x,y):
 cs=[c for c in heads if abs(c['x0']-x)<.6 and abs(oy(c)-y)<.18];assert len(cs)==1,(x,y,cs)
 return cs[0]
def note(x,y,staff,extraOctave=0):
 c=head(x,y);lines=staffs[staff]
 possible=[g for g in clefs if g['x0']<c['x0'] and lines[0]['top']-.2<=oy(g)<=lines[-1]['top']+.2]
 assert possible,(x,y,staff)
 g=max(possible,key=lambda z:z['x0']);spacing=c['size']/8
 base={'&':32,'V':32,'\uf0a0':32,'?':24,'t':24,'\uf0e6':24,'B':28}[g['text']]
 anchor=lines[3]['top'] if 'EngraverFontSet' in g['fontname'] and g['text']=='&' else oy(g)
 step=(anchor-oy(c))/spacing;diatonic=base+round(step);error=abs(step-round(step));assert error<.11,(x,y,step)
 octave,index=divmod(diatonic,7);letter='CDEFGAB'[index];pc=[0,2,4,5,7,9,11][index]
 # Accidental applies at the note's exact staff height, not to adjacent text.
 local=[a for a in music if a['text'] in ['#','b','n'] and 0<c['x0']-a['x0']<6 and abs(oy(a)-oy(c))<.18]
 acc=max(local,key=lambda a:a['x0'])['text'] if local else None
 # Key signatures at the start of the staff: retained letter identity across octaves.
 if acc is None:
  signatures=[a for a in music if a['text'] in ['#','b','n'] and 110<a['x0']<119 and lines[0]['top']-4<oy(a)<lines[-1]['top']+4]
  for a in signatures:
   astep=round((anchor-oy(a))/spacing);aindex=(base+astep)%7
   if aindex==index:acc=a['text']
 delta={'#':1,'b':-1,'n':0,None:0}[acc];midi=(octave+1)*12+pc+delta+12*extraOctave
 return {'name':letter+({'#':'#','b':'b','n':'',None:''}[acc])+str(octave+extraOctave),'writtenChromaticIndex':midi,
  'sourcePoint':{'x':c['x0'],'yFromTop':oy(c),'glyph':c['text'],'staffIndexZeroBased':staff,'clefGlyph':g['text'],'clefPoint':[g['x0'],oy(g)],'clefFont':g['fontname'],'interpretedClefAnchor':anchor,
   'staffHalfSpace':spacing,'diatonicRoundingError':error,'localAccidental':acc,'additionalOctaveAnnotation':extraOctave}}
# Source points are independently located vector glyphs, not invented range numbers.
# Each entry fixes the staff for each endpoint, including documented mid-staff clef changes.
SPECS=[
 ('soprano-sheng','Soprano Sheng','wind',0,(122.28,121.14,3),(150.36,102.96,3),None),
 ('tenor-sheng','Tenor Sheng','wind',0,(122.28,143.88,4),(150.36,125.70,4),None),
 ('bass-sheng','Bass Sheng','wind',0,(122.28,163.92,5),(150.36,147.54,5),None),
 ('soprano-suona','Soprano keyed Suona','wind',0,(122.28,190.50,6),(202.80,175.92,6),(225.30,175.02,6)),
 ('alto-suona','Alto keyed Suona','wind',0,(122.28,215.04,7),(202.80,200.46,7),(225.30,199.56,7)),
 ('tenor-suona','Tenor keyed Suona','wind',0,(122.28,235.08,8),(202.80,221.40,8),(225.30,220.50,8)),
 ('bass-suona','Bass keyed Suona','wind',0,(122.28,255.12,9),(202.80,244.20,9),(225.30,243.24,9)),
 ('contrabass-suona','Contrabass keyed Suona','wind',0,(342.30,258.72,9),(384.66,247.80,9),(403.86,246.00,9)),
 ('alto-guan','Alto keyed Guan','wind',-12,(122.28,312.42,11),(150.36,301.50,11),(177.12,296.94,11)),
 ('bass-guan','Bass keyed Guan','wind',0,(122.28,337.32,12),(150.36,327.30,12),(177.12,321.84,12)),
 ('contrabass-guan','Contrabass keyed Guan','wind',0,(434.64,314.28,11),(456.30,305.16,11),None),
 ('yangqin','Yangqin','plucked',0,(121.92,548.88,21),(151.50,514.92,20),None),
 ('liuqin','Xiaoruan / Liuqin','plucked',0,(150.36,582.24,22),(178.68,562.20,22),(220.74,559.50,22)),
 ('pipa','Pipa','plucked',0,(150.36,598.62,23),(178.38,586.80,23),None),
 ('zhongruan','Zhongruan','plucked',-12,(150.36,628.32,24),(178.08,613.74,24),(202.80,608.28,24)),
 ('daruan','Daruan','plucked',0,(150.36,646.50,25),(177.78,641.94,25),(202.80,637.38,25)),
 ('sanxian','Sanxian','plucked',0,(150.36,663.54,26),(177.30,658.08,26),(202.80,655.38,26)),
 ('gaohu','Gaohu','bowed',0,(150.36,727.86,29),(177.12,714.24,29),(203.16,711.48,29)),
 ('erhu','Erhu I, II','bowed',0,(150.36,752.46,30),(177.12,739.74,30),(202.80,736.08,30)),
 ('zhonghu','Zhonghu','bowed',0,(150.36,777.96,31),(177.12,767.94,31),(202.80,761.58,31)),
 ('gehu','Gehu','bowed',0,(150.36,798.90,32),(177.12,782.52,32),(202.80,786.12,32)),
 ('bass-gehu','Bass Gehu','bowed',-12,(150.36,818.88,33),(177.12,804.36,33),(202.80,808.92,33)),
 ('marimba','Marimba','percussion',0,(122.28,505.20,19),(189.66,470.88,18,1),None),
 ('vibraphone','Vibraphone','percussion',0,(238.98,503.34,19),(273.60,470.88,18,1),None),
 ('xylophone','Xylophone','percussion',12,(342.42,503.34,19),(375.60,470.88,18,1),None),
 ('glockenspiel','Glockenspiel','percussion',24,(436.62,487.26,18),(464.88,470.88,18),None),
 ('tubular-bells','Tubular Bells','percussion',0,(437.40,447.54,17),(465.00,438.42,17),None),
 ('yunluo','Yunluo','percussion',0,(122.28,413.94,15),(150.36,394.80,15),None),
 ('bianzhong','Bianzhong','percussion',0,(122.28,449.34,17),(150.36,416.28,16),None)]
profiles=[]
for key,label,family,transpose,lo,hi,extreme in SPECS:
 low=note(*lo);high=note(*hi);ex=note(*extreme) if extreme else None
 minimum=low['writtenChromaticIndex']+transpose;normalMax=high['writtenChromaticIndex']+transpose;maximum=(ex or high)['writtenChromaticIndex']+transpose
 assert minimum<=normalMax<=maximum,(key,minimum,normalMax,maximum)
 excluded=[minimum+1,maximum-1] if key=='bianzhong' else []
 # Chromatic index is staff-note arithmetic; no equal-tempered acousticHz inferred.
 members=[{'sourceSoundingChromaticIndex':i,'capability':'normal' if i<=normalMax else 'source-extreme-range','physicalFrequencyHz':None} for i in range(minimum,maximum+1) if i not in excluded]
 profiles.append({'id':key,'nativeName':label,'family':family,'writtenLow':low,'writtenNormalHigh':high,'writtenExtremeHigh':ex,
   'sourceWrittenToSoundingSemitones':transpose,'sourceSoundingMinimum':minimum,'sourceSoundingNormalMaximum':normalMax,'sourceSoundingMaximum':maximum,
   'excludedSoundingChromaticIndices':excluded,'members':members,'sourceSoundingNoteAddressCount':len(members),
   'boundary':'Source-qualified chromatic staff-note capability addresses. No measuredHz, physical instrument/performer multiplicity, execution or ancient tuning inferred.'})
by={p['id']:p for p in profiles}
assert by['yunluo']['sourceSoundingNoteAddressCount']==37
assert by['bianzhong']['sourceSoundingNoteAddressCount']==52
assert by['marimba']['sourceSoundingNoteAddressCount']==52
assert by['vibraphone']['sourceSoundingNoteAddressCount']==49
assert by['xylophone']['sourceSoundingNoteAddressCount']==49
assert by['glockenspiel']['sourceSoundingNoteAddressCount']==32
assert by['bass-gehu']['sourceSoundingMinimum']==28 # source E1, written E2, octave below
zhengPoints=[(122.28,706.26,28),(127.62,705.36,28),(132.78,704.46,28),(138.06,702.60,28),(142.62,701.70,28),
 (146.70,699.90,28),(150.96,699.00,28),(155.52,698.10,28),(160.08,696.24,28),(164.22,695.34,28),
 (170.46,686.34,27),(175.08,685.38,27),(179.82,684.48,27),(184.26,682.68,27),(189.42,681.78,27),
 (194.22,679.92,27),(198.54,679.02,27),(204.78,678.12,27),(210.60,676.32,27),(216.84,675.42,27),(222.72,673.56,27)]
zheng=[];owners={}
for i,point in enumerate(zhengPoints):
 n=note(*point);v=n['writtenChromaticIndex'];settings=[{'localShiftSemitones':s,'sourceSoundingChromaticIndex':v+s,'physicalFrequencyHz':None} for s in [-1,0,1]]
 zheng.append({'sourceOrdinalAscending':i+1,'openString':n,'localBridgeSettings':settings})
 for s in settings:owners.setdefault(s['sourceSoundingChromaticIndex'],[]).append(i+1)
assert len(zheng)==21 and len({z['openString']['writtenChromaticIndex'] for z in zheng})==21
assert len(owners)==51 and min(owners)==37 and max(owners)==87
assert all((z['openString']['writtenChromaticIndex']-38)%12 in [0,2,4,7,9] for z in zheng)
assert owners[37]==owners[38]==[1]
zhengControl={'sourceOpenStringOccurrences':21,'localSettingOccurrences':63,'distinctSoundingStaffNotesAcrossLocalSettings':51,
 'distinctPitchUnion':list(sorted(owners)),'sourceTimingCondition':'Move bridges before playing; allow time when changing keys. No during-note retuning inferred.',
 'singleStringAdmitsOneSettingAtATime':True,'conditionalIndependentGlobalTuningCount':3**21,
 'globalCountBoundary':'3^21 is conditional on all local shifts being jointly independently admissible; source does not prove the absence of mechanical/shared-tension constraints.',
 'sourceSpecialTuningException':'The Chinese caption explicitly excepts special tunings (特殊定弦例外). This local operation is applied only to the printed open-string configuration.',
 'simultaneousCounterexample':{'requiredPitchNames':['C#2','D2'],'chromaticIndices':[37,38],'individuallyAdmissible':True,'onlyAvailableStringOrdinals':[1],
  'jointlyAdmissibleUnderOneSettingPerString':False,'proof':'Both values have the same singleton owner {string1}. One string cannot hold two bridge settings simultaneously. Other strings cannot supply either value in the stated local ±1 domain.'}}
cropBounds=(235,675,585,715);cropText=page.crop(cropBounds).extract_text()
assert 'Each String (note) can be adjusted a half step higher / lower by moving the bridges prior to playing.' in cropText
(HERE/'hkco-zheng-operation-crop.txt').write_text(cropText+'\n',encoding='utf8')
out={'schema':'sunny.hkco-source-ranges.v1','sourceId':'chinese-expanded:hkco-range2025','sourcePath':'state/research/chinese-expanded/hkco-range2025.pdf',
 'sourceSha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'sourcePageZeroBased':0,'method':'PDF vector notehead origins and staff/clef coordinates; explicit source octave annotations/transpositions; separately reviewed rendered crops.',
 'octaveConditions':['Marimba/vibraphone high endpoints have an explicit8va annotation.','Xylophone octave-clefs add12 and its upper endpoint adds another explicit8va.',
 'Glockenspiel15ma clef adds24.','Alto Guan, Zhongruan and Bass Gehu sound12semitones below written; octave clef and prose are the same condition, not applied twice.'],
 'profiles':profiles,'profileCount':len(profiles),'instrumentQualifiedSoundingNoteAddresses':sum(len(p['members']) for p in profiles),
 'zhengOperationTextRegion':{'pageZeroBased':0,'cropBoundsPdfPoints':list(cropBounds),'textPath':'state/research/chinese-expanded/hkco-zheng-operation-crop.txt','textSha256':hashlib.sha256((cropText+'\n').encode('utf8')).hexdigest(),'transformation':'pdfplumber crop then extract_text; offsets refer to the extracted text, not PDF byte offsets.'},
 'zhengSourceStringsAndLocalOperations':zheng,'zhengOperationControl':zhengControl,
 'completeChartTranscription':False,'notEnumerated':['Non-keyed diatonic dizi/suona/Guan variants without an unrestricted chromatic-capability claim.',
 'Zheng joint performance is not a filled51-note simultaneous instrument: preserve21strings/63localsettings/51-pitch union separately.','Timpani/paigu continuous tuning and separate drum dimensions.',
 'The52bianzhong pitch values do not determine which physical bell/strike produces each one; detailed bell-map join remains unresolved.'],
 'validation':{'status':'passed','exit_code':0,'allGlyphOriginsMatch':True,'allStaffQuantizationErrorsBelow':.11,'sourceExplicitCardinalityControls':{'YunluoGongs':37,'BianzhongPitches':52},
 'computedKeyboardStaffSpans':[52,49,49,32],'zhengStrings':21,'zhengLocalSettings':63,'zhengPitchUnion':51,
 'sourcePitchToIndividualBellMap':False}}
(HERE/'hkco-source-ranges.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':'passed','exit_code':0,'profileCount':len(profiles),'instrumentQualifiedSoundingNoteAddresses':out['instrumentQualifiedSoundingNoteAddresses'],
 'profiles':[{k:p[k] for k in ['id','sourceSoundingMinimum','sourceSoundingNormalMaximum','sourceSoundingMaximum','sourceSoundingNoteAddressCount']} for p in profiles]},ensure_ascii=False,indent=2))

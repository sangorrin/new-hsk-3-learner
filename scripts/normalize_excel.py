import json, re, zipfile, xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
previous={}
generated_path=ROOT/'src/data/generated.json'
if generated_path.exists():
 try: previous=json.loads(generated_path.read_text(encoding='utf-8'))
 except json.JSONDecodeError: previous={}
previous_vocab={item.get('id'):item for item in previous.get('vocabulary',[])}
previous_sentences={item.get('id'):item for item in previous.get('sentences',[])}
previous_grammar={item.get('id'):item for item in previous.get('grammar',[])}
previous_grammar_phrases={item.get('id'):item for item in previous.get('grammarPhrases',[])}
previous_hanzi={item.get('char'):item for item in previous.get('hanzi',[])}
def cell(c):
 return ''.join(t.text or '' for t in c.findall('.//m:t',NS)) or (c.findtext('m:v',default='',namespaces=NS) or '')
def rows(path):
 out=[]
 with zipfile.ZipFile(path) as z:
  workbook=ET.fromstring(z.read('xl/workbook.xml'))
  rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
  relmap={r.attrib['Id']:r.attrib['Target'].lstrip('/') for r in rels}
  for sheet_ref in workbook.find('m:sheets',NS):
   sheet_name=sheet_ref.attrib['name']
   target=relmap[sheet_ref.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
   name='xl/'+target if not target.startswith('xl/') else target
   root=ET.fromstring(z.read(name)); sheet=[]
   for row in root.findall('.//m:sheetData/m:row',NS): sheet.append([cell(c) for c in row.findall('m:c',NS)])
   out.append((sheet_name,sheet))
 return out
vocab=[]; sentences=[]
for sheet_name, sheet in rows(ROOT/'REFERENCES/hsk3-vocabulary-complete-lessons-1-18.xlsx'):
 match=re.match(r'Lesson (\d+) Vocabulary$',sheet_name)
 if not match: continue
 lesson=int(match.group(1))
 header=next((i for i,r in enumerate(sheet) if r and r[0]=='No.' and len(r)>1 and r[1].startswith('Vocabulary')),None)
 for r in sheet[(header+1 if header is not None else 0):]:
  if len(r)>=8 and r[0].isdigit() and r[1]:
   item={'id':f'l{lesson}-v{r[0]}','lesson':lesson,'hanzi':r[1].strip(),'pinyin':r[2].strip(),'pos':r[3].strip(),'english':r[4].strip(),'section':r[5].strip(),'audio':r[6].strip(),'example':r[7].strip()}
   if previous_vocab.get(item['id'],{}).get('spanish'): item['spanish']=previous_vocab[item['id']]['spanish']
   vocab.append(item)
   if item['example']:
    old_sentence=previous_sentences.get(item['id'],{})
    sentences.append({'id':item['id'],'lesson':lesson,'hanzi':item['example'],'pinyin':old_sentence.get('pinyin',''),'english':old_sentence.get('english',''),'spanish':old_sentence.get('spanish',''),'source':item['hanzi']})
grammar=[]
grammar_phrases=[]
for sheet_name, sheet in rows(ROOT/'REFERENCES/hsk3-grammar-complete-lessons-1-18.xlsx'):
 match=re.match(r'Lesson (\d+) Grammar$',sheet_name)
 if not match: continue
 lesson=int(match.group(1))
 header=next((i for i,r in enumerate(sheet) if r and r[0]=='Point No.'),None)
 for r in sheet[(header+1 if header is not None else 0):]:
  if len(r)>=7 and r[0].isdigit():
   grammar_id=f'l{lesson}-g{r[0]}'
   grammar_item={'id':grammar_id,'lesson':lesson,'point':r[1].strip(),'name':r[2].strip(),'formula':r[3].strip(),'notes':r[4].strip(),'examples':r[5].strip(),'translations':r[6].strip()}
   old_grammar=previous_grammar.get(grammar_id,{})
   for key in ('spanishName','spanishNotes'):
    if old_grammar.get(key): grammar_item[key]=old_grammar[key]
   grammar.append(grammar_item)
   examples=[line.strip() for line in r[5].splitlines() if line.strip()]
   translations=[line.strip() for line in r[6].splitlines() if line.strip()]
   for idx, example in enumerate(examples):
    phrase_id=f'l{lesson}-g{r[0]}-p{idx+1}'
    phrase={'id':phrase_id,'lesson':lesson,'hanzi':re.sub(r'^\d+\.\s*','',example),'english':re.sub(r'^\d+\.\s*','',translations[idx]) if idx < len(translations) else '','source':r[1].strip()}
    if previous_grammar_phrases.get(phrase_id,{}).get('spanish'): phrase['spanish']=previous_grammar_phrases[phrase_id]['spanish']
    grammar_phrases.append(phrase)
chars=[]
for s in [v['hanzi'] for v in vocab]+[v['example'] for v in vocab]:
 for ch in s:
  if '\u3400' <= ch <= '\u9fff' and ch not in chars: chars.append(ch)
hanzi=[]
for i,ch in enumerate(chars,1):
 related=[v for v in vocab if ch in v['hanzi']]
 item={'id':i,'char':ch,'lesson':related[0]['lesson'] if related else 1,'words':[v['hanzi'] for v in related[:8]]}
 old_hanzi=previous_hanzi.get(ch,{})
 for key in ('meaningEnglish','meaningSpanish'):
  if old_hanzi.get(key): item[key]=old_hanzi[key]
 hanzi.append(item)
out={'vocabulary':vocab,'sentences':sentences,'grammar':grammar,'grammarPhrases':grammar_phrases,'hanzi':hanzi}
(ROOT/'src/data').mkdir(exist_ok=True)
(ROOT/'src/data/generated.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'vocabulary={len(vocab)} sentences={len(sentences)} grammar={len(grammar)} grammar_phrases={len(grammar_phrases)} hanzi={len(hanzi)}')

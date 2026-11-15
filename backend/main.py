from fastapi import FastAPI,HTTPException,Depends,Header,UploadFile,File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from pathlib import Path
from datetime import datetime,timezone,timedelta
import sqlite3,secrets,hashlib,json,re,uuid,os,random
from pypdf import PdfReader
from docx import Document
BASE=Path(__file__).resolve().parent.parent; DATA=Path(os.environ.get('DATA_DIR',str(BASE/'backend'/'data'))); FILES=DATA/'uploads'; DB=DATA/'platform.sqlite3'; DATA.mkdir(parents=True,exist_ok=True); FILES.mkdir(parents=True,exist_ok=True)
app=FastAPI(title='TalentLens API',version='1.0'); app.mount('/static',StaticFiles(directory=BASE/'frontend'),name='static')
def now():return datetime.now(timezone.utc).isoformat(timespec='seconds')
def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON');return c
def ph(p,s=None):
 s=s or secrets.token_hex(16);return s+'$'+hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(s),180000).hex()
def verify(p,h):
 s,_=h.split('$',1);return secrets.compare_digest(ph(p,s),h)
SKILLS=['python','sql','java','javascript','react','typescript','node.js','html','css','machine learning','deep learning','nlp','tensorflow','pytorch','scikit-learn','data analysis','pandas','numpy','power bi','aws','docker','git','fastapi','django','communication','leadership','project management','angular','angularjs','c++','c#','rest api','linux','excel']
ALIASES={'js':'javascript','nodejs':'node.js','ml':'machine learning','postgres':'postgresql','reactjs':'react','py':'python','sklearn':'scikit-learn'}
OLD={'angularjs':('angular','Legacy framework name; confirm current Angular experience.'),'python 2':('python 3','Python 2 is end-of-life; confirm current Python experience.'),'flash':('html5','Flash is obsolete; confirm current web skills.')}
def canon(s):
 s=re.sub(r'\s+',' ',str(s).lower().strip());return ALIASES.get(s,s)
def skills_in(t):
 l=canon(t);return sorted({s for s in SKILLS if re.search(r'(?<![a-z0-9])'+re.escape(s)+r'(?![a-z0-9])',l)})

def tfidf_similarity(a,b):
 import math,re
 from collections import Counter
 def terms(s):
  w=re.findall(r"[a-z0-9+#.]+",s.lower());return w+[w[i]+' '+w[i+1] for i in range(len(w)-1)]
 docs=[terms(a),terms(b)];counts=[Counter(d) for d in docs];v=[]
 for c in counts:
  v.append({t:n*(math.log(3/(1+sum(t in x for x in counts)))+1) for t,n in c.items()})
 dot=sum(x*v[1].get(t,0) for t,x in v[0].items());den=math.sqrt(sum(x*x for x in v[0].values())*sum(x*x for x in v[1].values()))
 return 100*dot/den if den else 0


def tfidf_similarity(a,b):
 import math,re
 from collections import Counter
 def terms(s):
  w=re.findall(r"[a-z0-9+#.]+",s.lower());return w+[w[i]+' '+w[i+1] for i in range(len(w)-1)]
 docs=[terms(a),terms(b)];counts=[Counter(d) for d in docs];v=[]
 for c in counts:
  v.append({t:n*(math.log(3/(1+sum(t in x for x in counts)))+1) for t,n in c.items()})
 dot=sum(x*v[1].get(t,0) for t,x in v[0].items());den=math.sqrt(sum(x*x for x in v[0].values())*sum(x*x for x in v[1].values()))
 return 100*dot/den if den else 0


def tfidf_similarity(a,b):
 import math,re
 from collections import Counter
 def terms(s):
  w=re.findall(r"[a-z0-9+#.]+",s.lower());return w+[w[i]+' '+w[i+1] for i in range(len(w)-1)]
 docs=[terms(a),terms(b)];counts=[Counter(d) for d in docs];v=[]
 for c in counts:
  v.append({t:n*(math.log(3/(1+sum(t in x for x in counts)))+1) for t,n in c.items()})
 dot=sum(x*v[1].get(t,0) for t,x in v[0].items());den=math.sqrt(sum(x*x for x in v[0].values())*sum(x*x for x in v[1].values()))
 return 100*dot/den if den else 0

def score(text,req,evid,assessment=None):
 claims={canon(x) for x in skills_in(text)}; ev={canon(x['skill']) for x in evid}; weight=sum(float(x.get('weight',.7)) for x in req) or 1
 coverage=100*sum(float(x.get('weight',.7)) for x in req if canon(x['name']) in claims)/weight
 evcov=100*sum(float(x.get('weight',.7)) for x in req if canon(x['name']) in ev)/weight
 sim=tfidf_similarity(text, ' '.join(x['name'] for x in req))
 parts=[(coverage,.45),(sim,.20),(evcov,.15)]+([(assessment,.20)] if assessment is not None else []); total=sum(w for _,w in parts);match=round(sum(v*w for v,w in parts)/total,1)
 consistency=100 if assessment is None else max(0,100-abs(coverage-assessment)); completeness=min(100,40+min(60,len(text.strip())/18));trust=round(.5*evcov+.25*consistency+.25*completeness,1)
 skill_map=[];matched=[];missing=[]
 for x in req:
  name=x['name'];found=canon(name) in claims;has=canon(name) in ev
  (matched if found else missing).append(name)
  fresh={'status':'current','note':'No legacy rule triggered; this is not a live technology check.'}
  if canon(name) in OLD:fresh={'status':'review','note':OLD[canon(name)][1],'successor':OLD[canon(name)][0]}
  skill_map.append({'skill':name,'resume_match':found,'evidence_added':has,'note':next((e['title'] for e in evid if canon(e['skill'])==canon(name)),None),'freshness':fresh})
 tips=[f'Add project, certificate or portfolio evidence for {x}.' for x in missing[:3]]
 if assessment is not None and assessment+25<coverage:tips.append('Your quiz result is below resume skill coverage; practice those skills before applying again.')
 if sim<25:tips.append('Tailor your resume to describe relevant work and project outcomes.')
 return {'match':match,'trust':trust,'skill_coverage':round(coverage,1),'text_similarity':round(sim,1),'evidence_coverage':round(evcov,1),'assessment':assessment,'matched_skills':matched,'missing_skills':missing,'skill_map':skill_map,'contributions':[{'label':'Required skills in resume','value':round(coverage,1)},{'label':'Job text similarity · TF-IDF','value':round(sim,1)},{'label':'Supporting evidence provided','value':round(evcov,1)}]+([{'label':'Role skill check','value':round(assessment,1)}] if assessment is not None else []),'recommendations':tips,'human_review':'Scores organize evidence for review. They do not establish candidate quality or make a hiring decision.'}
def questions(req,custom=None):
 chosen=[{**item,'kind':'recruiter'} for item in (custom or [])]
 random.shuffle(chosen)
 return chosen
def setup():
 with db() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT,email TEXT UNIQUE,password TEXT,role TEXT,created TEXT,approval_status TEXT NOT NULL DEFAULT 'approved');CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user_id INT,expires TEXT);CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY,recruiter INT,title TEXT,company TEXT,location TEXT,description TEXT,skills TEXT,created TEXT,status TEXT DEFAULT 'open');CREATE TABLE IF NOT EXISTS resumes(id INTEGER PRIMARY KEY,user_id INT,filename TEXT,filekey TEXT,text TEXT,skills TEXT,version INT,created TEXT,deleted INTEGER NOT NULL DEFAULT 0);CREATE TABLE IF NOT EXISTS evidence(id INTEGER PRIMARY KEY,user_id INT,skill TEXT,title TEXT,kind TEXT,url TEXT,description TEXT,created TEXT);CREATE TABLE IF NOT EXISTS apps(id INTEGER PRIMARY KEY,job_id INT,user_id INT,resume_id INT,match REAL,trust REAL,scores TEXT,status TEXT,created TEXT,UNIQUE(job_id,user_id));CREATE TABLE IF NOT EXISTS tests(id INTEGER PRIMARY KEY,app_id INT UNIQUE,questions TEXT,score REAL,completed TEXT);CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY,app_id INT UNIQUE,recruiter INT,decision TEXT,note TEXT,created TEXT);''')
  cols={r['name'] for r in c.execute('pragma table_info(users)').fetchall()}
  if 'approval_status' not in cols:c.execute("alter table users add column approval_status TEXT NOT NULL DEFAULT 'approved'")
  job_cols={r['name'] for r in c.execute('pragma table_info(jobs)').fetchall()}
  if 'approval_status' not in job_cols:c.execute("alter table jobs add column approval_status TEXT NOT NULL DEFAULT 'pending'")
  if 'assessment_questions' not in job_cols:c.execute("alter table jobs add column assessment_questions TEXT NOT NULL DEFAULT '[]'")
  resume_cols={r['name'] for r in c.execute('pragma table_info(resumes)').fetchall()}
  if resume_cols and 'deleted' not in resume_cols:c.execute('alter table resumes add column deleted INTEGER NOT NULL DEFAULT 0')
  if c.execute('select count(*) from users').fetchone()[0]==0:
   if os.environ.get('DEMO_MODE','true').lower()!='true':
    email=os.environ.get('ADMIN_EMAIL','').strip().lower();password=os.environ.get('ADMIN_PASSWORD','')
    if not email or len(password)<12:raise RuntimeError('Set ADMIN_EMAIL and an ADMIN_PASSWORD of at least 12 characters before production startup.')
    c.execute('insert into users(name,email,password,role,created,approval_status) values(?,?,?,?,?,?)',(os.environ.get('ADMIN_NAME','Platform Admin'),email,ph(password),'admin',now(),'approved'))
    return
   def add(n,e,r):c.execute("insert into users(name,email,password,role,created,approval_status) values(?,?,?,?,?, 'approved')",(n,e,ph('Demo123!'),r,now()));return c.execute('select last_insert_rowid()').fetchone()[0]
   rid=add('Maya Recruiter','recruiter@demo.com','recruiter');cid=add('Aarav Candidate','candidate@demo.com','candidate');add('Admin Demo','admin@demo.com','admin')
   req=[{'name':'Python','weight':1,'level':'intermediate'},{'name':'SQL','weight':.8,'level':'intermediate'},{'name':'Machine Learning','weight':.8,'level':'intermediate'},{'name':'FastAPI','weight':.7,'level':'beginner'}]
   c.execute('insert into jobs(recruiter,title,company,location,description,skills,created) values(?,?,?,?,?,?,?)',(rid,'Junior AI Engineer','Northstar Labs','Bengaluru · Hybrid','Build Python and machine learning services. Use SQL, evaluate models and develop REST APIs with the product team.',json.dumps(req),now()));jid=c.execute('select last_insert_rowid()').fetchone()[0]
   txt='Aarav Kumar MCA student with Python SQL machine learning FastAPI. Built student performance prediction using pandas and scikit-learn. Developed REST API for model inference. Presented a capstone project to a team.'
   c.execute('insert into resumes(user_id,filename,text,skills,version,created) values(?,?,?,?,?,?)',(cid,'Aarav_Kumar_MCA_Resume.pdf',txt,json.dumps(skills_in(txt)),1,now()));res=c.execute('select last_insert_rowid()').fetchone()[0]
   c.execute('insert into evidence(user_id,skill,title,kind,url,description,created) values(?,?,?,?,?,?,?)',(cid,'Python','Student performance prediction','project','https://github.com/','Demo candidate-submitted evidence.',now()))
   evrows=c.execute('select * from evidence where user_id=?',(cid,)).fetchall();ss=score(txt,req,evrows,None);c.execute('insert into apps(job_id,user_id,resume_id,match,trust,scores,status,created) values(?,?,?,?,?,?,?,?)',(jid,cid,res,ss['match'],ss['trust'],json.dumps(ss),'applied',now()));aid=c.execute('select last_insert_rowid()').fetchone()[0];c.execute('insert into tests(app_id,questions) values(?,?)',(aid,json.dumps(questions(req))))
  pending=c.execute('select t.app_id,t.questions,j.skills,j.assessment_questions from tests t join apps a on a.id=t.app_id join jobs j on j.id=a.job_id where t.completed is null').fetchall()
  for test in pending:
   old=json.loads(test['questions'] or '[]')
   custom=json.loads(test['assessment_questions'] or '[]')
   if len(old)!=len(custom) or any(q.get('kind')!='recruiter' for q in old):
    c.execute('update tests set questions=? where app_id=?',(json.dumps(questions(json.loads(test['skills']),json.loads(test['assessment_questions'] or '[]'))),test['app_id']))
class Login(BaseModel):email:str;password:str
class Signup(BaseModel):name:str=Field(min_length=2);email:str;password:str=Field(min_length=8);role:str='candidate'
class Approval(BaseModel):status:str
class AdminUserIn(BaseModel):name:str=Field(min_length=2);email:str;password:str=Field(min_length=8);role:str
class JobIn(BaseModel):title:str;company:str;location:str='';description:str;skills:list[dict];assessment_questions:list[dict]=Field(default_factory=list)
class SkillSuggestIn(BaseModel):description:str
class EvidenceIn(BaseModel):skill:str;title:str;kind:str='project';url:str='';description:str=''
class ApplyIn(BaseModel):resume_id:int
class Answers(BaseModel):answers:list[int]
class FeedbackIn(BaseModel):decision:str;note:str=''
@app.on_event('startup')
def start():setup()
@app.get('/')
def home():return FileResponse(BASE/'frontend'/'index.html')
def auth(authorization:str|None=Header(None)):
 if not authorization or not authorization.lower().startswith('bearer '):raise HTTPException(401,'Sign in to continue.')
 with db() as c:r=c.execute('select u.* from sessions s join users u on u.id=s.user_id where s.token=? and s.expires>?',(authorization.split(' ',1)[1],now())).fetchone()
 if not r:raise HTTPException(401,'Session expired. Sign in again.')
 return dict(r)
def role(u,*rs):
 if u['role'] not in rs:raise HTTPException(403,'This action is unavailable for your account role.')
@app.post('/api/auth/login')
def login(x:Login):
 with db() as c:u=c.execute('select * from users where lower(email)=lower(?)',(x.email.strip(),)).fetchone()
 if not u or not verify(x.password,u['password']):raise HTTPException(401,'Email or password is incorrect.')
 if u['approval_status']=='pending':raise HTTPException(403,'Your account is waiting for administrator approval.')
 if u['approval_status']!='approved':raise HTTPException(403,'This account was not approved. Contact the administrator.')
 t=secrets.token_urlsafe(32)
 with db() as c:c.execute('insert into sessions values(?,?,?)',(t,u['id'],(datetime.now(timezone.utc)+timedelta(hours=12)).isoformat()))
 return {'token':t,'user':{k:u[k] for k in ('id','name','email','role')}}
@app.post('/api/auth/register')
def signup(x:Signup):
 if x.role not in ('candidate','recruiter'):raise HTTPException(400,'Choose candidate or recruiter. Administrator accounts are created by the platform owner.')
 if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',x.email):raise HTTPException(400,'Enter a valid email.')
 try:
  with db() as c:c.execute("insert into users(name,email,password,role,created,approval_status) values(?,?,?,?,?,'pending')",(x.name.strip(),x.email.strip().lower(),ph(x.password),x.role,now()))
 except sqlite3.IntegrityError:raise HTTPException(409,'Email already registered.')
 return {'pending_approval':True,'message':'Registration received. An administrator must approve this account before sign-in is enabled.'}
@app.post('/api/auth/logout')
def logout(u=Depends(auth),authorization:str|None=Header(None)):
 with db() as c:c.execute('delete from sessions where token=?',(authorization.split(' ',1)[1],))
 return {'ok':True}
@app.get('/api/me')
def me(u=Depends(auth)):
 with db() as c:r=c.execute('select id,name,email,role,approval_status from users where id=?',(u['id'],)).fetchone()
 return dict(r)
@app.get('/api/health')
def health():return {'ok':True,'database':'SQLite','service':'TalentLens','demo_mode':os.environ.get('DEMO_MODE','true').lower()=='true'}
@app.get('/api/jobs')
def listjobs(u=Depends(auth)):
 with db() as c:
  select='select j.*,j.recruiter recruiter_id,u.name recruiter_name,u.email recruiter_email,(select count(*) from apps a where a.job_id=j.id) applicant_count from jobs j join users u on u.id=j.recruiter'
  if u['role']=='admin':rows=c.execute(select).fetchall()
  elif u['role']=='recruiter':rows=c.execute(select+' where j.recruiter=? and j.status="open"',(u['id'],)).fetchall()
  else:rows=c.execute(select+' where j.status="open" and j.approval_status="approved"').fetchall()
 out=[]
 for r in rows:
  item=dict(r,skills=json.loads(r['skills']),assessment_question_count=len(json.loads(r['assessment_questions'] or '[]')))
  if u['role'] in ('recruiter','admin'):item['assessment_questions']=json.loads(r['assessment_questions'] or '[]')
  else:item.pop('assessment_questions',None)
  out.append(item)
 return out
@app.post('/api/jobs/suggest-skills')
def suggest_job_skills(x:SkillSuggestIn,u=Depends(auth)):
 role(u,'recruiter','admin')
 text=x.description.lower()[:5000];out=[]
 for name in skills_in(text):
  escaped=re.escape(name)
  important=bool(re.search(r'(?:required|must[- ]have|essential|critical|proficient in|expert in)[^.!?]{0,45}'+escaped,text) or re.search(escaped+r'[^.!?]{0,25}(?:required|essential|must[- ]have)',text))
  out.append({'name':name,'weight':1 if important else .8,'level':'intermediate'})
 return {'skills':out}
def clean_questions(items):
 out=[]
 for item in items[:20]:
  text=str(item.get('question','')).strip();opts=[str(v).strip() for v in item.get('options',[]) if str(v).strip()]
  try:answer=int(item.get('answer',-1))
  except (TypeError,ValueError):answer=-1
  if not text or len(text)>500 or len(opts)<2 or len(opts)>5 or answer<0 or answer>=len(opts):raise HTTPException(400,'Each custom question needs text, 2–5 options, and a valid correct answer.')
  out.append({'skill':'Role question','question':text,'options':opts,'answer':answer,'kind':'recruiter'})
 return out
@app.post('/api/jobs')
def newjob(x:JobIn,u=Depends(auth)):
 role(u,'recruiter','admin')
 req=[{'name':str(s.get('name','')).strip(),'weight':max(.1,min(1,float(s.get('weight',.7)))),'level':s.get('level','intermediate')} for s in x.skills if str(s.get('name','')).strip()]
 if not req:raise HTTPException(400,'Add at least one required skill.')
 custom=clean_questions(x.assessment_questions)
 with db() as c:c.execute('insert into jobs(recruiter,title,company,location,description,skills,created,approval_status,assessment_questions) values(?,?,?,?,?,?,?,?,?)',(u['id'],x.title,x.company,x.location,x.description,json.dumps(req),now(),'approved' if u['role']=='admin' else 'pending',json.dumps(custom)))
 return {'ok':True,'approval_status':'approved' if u['role']=='admin' else 'pending'}
@app.put('/api/jobs/{jid}')
def resubmit_job(jid:int,x:JobIn,u=Depends(auth)):
 role(u,'recruiter')
 req=[{'name':str(s.get('name','')).strip(),'weight':max(.1,min(1,float(s.get('weight',.7)))),'level':s.get('level','intermediate')} for s in x.skills if str(s.get('name','')).strip()]
 if not req:raise HTTPException(400,'Add at least one required skill.')
 custom=clean_questions(x.assessment_questions)
 with db() as c:
  job=c.execute('select recruiter,status,approval_status from jobs where id=?',(jid,)).fetchone()
  if not job:raise HTTPException(404,'Role not found.')
  if job['recruiter']!=u['id']:raise HTTPException(403,'Not your role.')
  if job['status']!='open':raise HTTPException(400,'Closed roles cannot be resubmitted.')
  if job['approval_status']!='rejected':raise HTTPException(400,'Only rejected roles can be revised and resubmitted.')
  c.execute('update jobs set title=?,company=?,location=?,description=?,skills=?,assessment_questions=?,approval_status="pending" where id=?',(x.title.strip(),x.company.strip(),x.location.strip(),x.description.strip(),json.dumps(req),json.dumps(custom),jid))
 return {'ok':True,'approval_status':'pending'}
@app.delete('/api/jobs/{jid}')
def closejob(jid:int,u=Depends(auth)):
 role(u,'recruiter','admin')
 with db() as c:r=c.execute('select recruiter from jobs where id=?',(jid,)).fetchone()
 if not r:raise HTTPException(404,'Role not found.')
 if u['role']!='admin' and r['recruiter']!=u['id']:raise HTTPException(403,'Not your role.')
 with db() as c:c.execute('update jobs set status="closed" where id=?',(jid,))
 return {'ok':True}
@app.get('/api/resumes')
def listres(u=Depends(auth)):
 role(u,'candidate','admin')
 with db() as c:rs=c.execute('select id,filename,skills,version,created,deleted from resumes where user_id=? order by version desc',(u['id'],)).fetchall()
 return [dict(r,skills=json.loads(r['skills'])) for r in rs]
@app.post('/api/resumes')
async def upload(file:UploadFile=File(...),u=Depends(auth)):
 role(u,'candidate');ext=Path(file.filename or '').suffix.lower()
 if ext not in('.pdf','.docx'):raise HTTPException(400,'Upload PDF or DOCX.')
 raw=await file.read()
 if not raw or len(raw)>8*1024*1024:raise HTTPException(400,'File is empty or over 8 MB.')
 key=str(uuid.uuid4())+ext;path=FILES/key;path.write_bytes(raw)
 try:text='\n'.join(p.extract_text() or '' for p in PdfReader(str(path)).pages) if ext=='.pdf' else '\n'.join(p.text for p in Document(str(path)).paragraphs)
 except Exception:path.unlink(missing_ok=True);raise HTTPException(400,'Could not read that document.')
 if len(text.strip())<30:path.unlink(missing_ok=True);raise HTTPException(400,'No selectable text found. Scanned PDFs need OCR and are not supported in this demo.')
 with db() as c:ver=c.execute('select coalesce(max(version),0)+1 from resumes where user_id=?',(u['id'],)).fetchone()[0];c.execute('insert into resumes(user_id,filename,filekey,text,skills,version,created) values(?,?,?,?,?,?,?)',(u['id'],Path(file.filename).name,key,text,json.dumps(skills_in(text)),ver,now()));rid=c.execute('select last_insert_rowid()').fetchone()[0]
 return {'id':rid,'version':ver,'filename':Path(file.filename).name,'skills':skills_in(text)}
@app.delete('/api/resumes/{resume_id}')
def delete_resume(resume_id:int,u=Depends(auth)):
 role(u,'candidate')
 with db() as c:
  r=c.execute('select * from resumes where id=? and user_id=? and deleted=0',(resume_id,u['id'])).fetchone()
  if not r:raise HTTPException(404,'Resume not found.')
  if r['filekey']:
   (FILES/r['filekey']).unlink(missing_ok=True)
  c.execute("update resumes set filename=?,filekey=NULL,text='[This candidate deleted the resume file.]',skills='[]',deleted=1 where id=?",(f'Deleted resume · v{r["version"]}',resume_id))
 return {'ok':True,'message':'The uploaded file was deleted. Existing application scores remain as historical records.'}
@app.get('/api/evidence')
def listev(u=Depends(auth)):
 role(u,'candidate','admin')
 with db() as c:rs=c.execute('select * from evidence where user_id=? order by created desc',(u['id'],)).fetchall()
 return [dict(r) for r in rs]
@app.post('/api/evidence')
def addev(x:EvidenceIn,u=Depends(auth)):
 role(u,'candidate')
 if not x.skill.strip() or not x.title.strip():raise HTTPException(400,'Skill and title are required.')
 with db() as c:
  c.execute('insert into evidence(user_id,skill,title,kind,url,description,created) values(?,?,?,?,?,?,?)',(u['id'],x.skill.strip(),x.title.strip(),x.kind,x.url,x.description,now()))
  apps=c.execute('select a.*,j.skills,r.text from apps a join jobs j on j.id=a.job_id join resumes r on r.id=a.resume_id where a.user_id=?',(u['id'],)).fetchall()
  ev=c.execute('select * from evidence where user_id=?',(u['id'],)).fetchall()
  for a in apps:
   t=c.execute('select score from tests where app_id=?',(a['id'],)).fetchone();sc=score(a['text'],json.loads(a['skills']),ev,t['score'] if t else None);c.execute('update apps set match=?,trust=?,scores=? where id=?',(sc['match'],sc['trust'],json.dumps(sc),a['id']))
 return {'ok':True}
@app.delete('/api/evidence/{eid}')
def dele(eid:int,u=Depends(auth)):
 with db() as c:c.execute('delete from evidence where id=? and user_id=?',(eid,u['id']))
 return {'ok':True}
@app.get('/api/applications')
def applications(u=Depends(auth)):
 with db() as c:
  if u['role']=='candidate':rs=c.execute('select a.*,j.title job_title,j.company,j.skills job_skills,j.description,r.version resume_version,r.deleted resume_deleted from apps a join jobs j on j.id=a.job_id join resumes r on r.id=a.resume_id where a.user_id=? order by a.created desc',(u['id'],)).fetchall()
  elif u['role']=='recruiter':rs=c.execute('select a.*,j.title job_title,j.company,j.skills job_skills,j.description,u2.name candidate_name,u2.email candidate_email,r.filename resume_filename,r.skills resume_skills,r.version resume_version from apps a join jobs j on j.id=a.job_id join users u2 on u2.id=a.user_id join resumes r on r.id=a.resume_id where j.recruiter=? order by a.match desc',(u['id'],)).fetchall()
  else:rs=c.execute('select a.*,j.title job_title,j.company,u2.name candidate_name,u2.email candidate_email from apps a join jobs j on j.id=a.job_id join users u2 on u2.id=a.user_id order by a.match desc').fetchall()
  out=[]
  for r in rs:
   d=dict(r);d['match_score']=d['match'];d['trust_score']=d['trust'];scores=json.loads(d.pop('scores'));d['skills']=json.loads(d.pop('job_skills')) if 'job_skills' in d else [];d['resume_skills']=json.loads(d['resume_skills']) if 'resume_skills' in d else []
   skill_map=scores.get('skill_map',[]) or [];legacy_skills=[]
   normalized_skills=[]
   for skill in skill_map:
    if isinstance(skill,str):legacy_skills.append(skill)
    elif isinstance(skill,dict):
     freshness=skill.get('freshness') or {}
     normalized_skills.append({**skill,'freshness':{**freshness,'status':freshness.get('status') or 'current'}})
    else:raise ValueError('Stored application score contains an invalid skill entry.')
   known_skills={str(skill.get('skill','')).casefold() for skill in normalized_skills}
   for skill in legacy_skills:
    if skill.casefold() not in known_skills:
     normalized_skills.append({'skill':skill,'resume_match':True,'evidence_added':False,'note':None,'freshness':{'status':'current','note':'No legacy rule triggered; this is not a live technology check.'}})
     known_skills.add(skill.casefold())
   scores['skill_map']=normalized_skills;d['scores']=scores
   t=c.execute('select score,completed,questions from tests where app_id=?',(r['id'],)).fetchone();d['assessment_score']=t['score'] if t else None;d['assessment_completed']=bool(t and t['completed']);d['assessment_available']=bool(t and json.loads(t['questions'] or '[]'));f=c.execute('select decision,note from feedback where app_id=?',(r['id'],)).fetchone();d['feedback']=({'decision':f['decision']} if u['role']=='candidate' else dict(f)) if f else None;out.append(d)
 return out
@app.post('/api/jobs/{jid}/apply')
def apply(jid:int,x:ApplyIn,u=Depends(auth)):
 role(u,'candidate')
 with db() as c:
  j=c.execute('select j.* from jobs j where j.id=? and j.status="open" and j.approval_status="approved"',(jid,)).fetchone();r=c.execute('select * from resumes where id=? and user_id=? and deleted=0',(x.resume_id,u['id'])).fetchone()
  if not j or not r:raise HTTPException(404,'Role or resume not found.')
  ev=c.execute('select * from evidence where user_id=?',(u['id'],)).fetchall();sc=score(r['text'],json.loads(j['skills']),ev)
  try:c.execute('insert into apps(job_id,user_id,resume_id,match,trust,scores,status,created) values(?,?,?,?,?,?,?,?)',(jid,u['id'],x.resume_id,sc['match'],sc['trust'],json.dumps(sc),'applied',now()))
  except sqlite3.IntegrityError:raise HTTPException(409,'You already applied to this role.')
  aid=c.execute('select last_insert_rowid()').fetchone()[0];c.execute('insert into tests(app_id,questions) values(?,?)',(aid,json.dumps(questions(json.loads(j['skills']),json.loads(j['assessment_questions'] or '[]')))))
 return {'ok':True,'application_id':aid,'scores':sc}
@app.post('/api/applications/{aid}/resubmit')
def resubmit(aid:int,u=Depends(auth)):
 role(u,'candidate')
 with db() as c:
  a=c.execute('select * from apps where id=? and user_id=?',(aid,u['id'])).fetchone()
  if not a:raise HTTPException(404,'Application not found.')
  r=c.execute('select * from resumes where user_id=? and deleted=0 order by version desc limit 1',(u['id'],)).fetchone()
  if not r:raise HTTPException(400,'Upload a resume first.')
  job=c.execute('select skills,assessment_questions from jobs where id=?',(a['job_id'],)).fetchone();req=json.loads(job['skills']);ev=c.execute('select * from evidence where user_id=?',(u['id'],)).fetchall();sc=score(r['text'],req,ev,None)
  c.execute('update apps set resume_id=?,match=?,trust=?,scores=?,status="applied" where id=?',(r['id'],sc['match'],sc['trust'],json.dumps(sc),aid));c.execute('update tests set questions=?,score=NULL,completed=NULL where app_id=?',(json.dumps(questions(req,json.loads(job['assessment_questions'] or '[]'))),aid))
 return {'ok':True,'resume_version':r['version'],'scores':sc}
@app.get('/api/applications/{aid}/resume')
def resume_text(aid:int,u=Depends(auth)):
 with db() as c:
  a=c.execute('select a.user_id,a.resume_id,j.recruiter from apps a join jobs j on j.id=a.job_id where a.id=?',(aid,)).fetchone()
  if not a:raise HTTPException(404,'Application not found.')
  if u['role']=='candidate' and a['user_id']!=u['id']:raise HTTPException(403,'Not your application.')
  if u['role']=='recruiter' and a['recruiter']!=u['id']:raise HTTPException(403,'Not your application.')
  r=c.execute('select filename,text,deleted from resumes where id=?',(a['resume_id'],)).fetchone()
 return {'filename':r['filename'],'text':r['text'],'deleted':bool(r['deleted'])}
@app.get('/api/applications/{aid}/detail')
def detail(aid:int,u=Depends(auth)):
 with db() as c:
  a=c.execute('select a.*,j.title job_title,j.company,j.recruiter,u.name candidate_name from apps a join jobs j on j.id=a.job_id join users u on u.id=a.user_id where a.id=?',(aid,)).fetchone()
  if not a:raise HTTPException(404,'Application not found.')
  if u['role']=='candidate' and a['user_id']!=u['id']:raise HTTPException(403,'Not your application.')
  if u['role']=='recruiter' and a['recruiter']!=u['id']:raise HTTPException(403,'Not your application.')
  ev=c.execute('select skill,title,kind,url,description from evidence where user_id=?',(a['user_id'],)).fetchall();return {'application':dict(a),'evidence':[dict(x) for x in ev]}
@app.get('/api/applications/{aid}/assessment')
def gettest(aid:int,u=Depends(auth)):
 with db() as c:
  a=c.execute('select * from apps where id=?',(aid,)).fetchone();t=c.execute('select * from tests where app_id=?',(aid,)).fetchone()
  if not a or not t:raise HTTPException(404,'Assessment not found.')
  if u['role']=='candidate' and a['user_id']!=u['id']:raise HTTPException(403,'Not your application.')
  qs=json.loads(t['questions']);return {'available':bool(qs),'completed':bool(t['completed']),'score':t['score'],'total':len(qs),'questions':[{'skill':q['skill'],'question':q['question'],'options':q['options']} for q in qs]}
@app.post('/api/applications/{aid}/assessment')
def subtest(aid:int,x:Answers,u=Depends(auth)):
 role(u,'candidate')
 with db() as c:
  a=c.execute('select * from apps where id=? and user_id=?',(aid,u['id'])).fetchone();t=c.execute('select * from tests where app_id=?',(aid,)).fetchone()
  if not a or not t:raise HTTPException(404,'Assessment not found.')
  if t['completed']:raise HTTPException(409,'Assessment already submitted.')
  qs=json.loads(t['questions'])
  if not qs:raise HTTPException(400,'This role has no recruiter-added assessment questions.')
  if len(qs)!=len(x.answers):raise HTTPException(400,'Answer every question.')
  correct=sum(q['answer']==v for q,v in zip(qs,x.answers));val=round(100*correct/max(1,len(qs)),1);c.execute('update tests set score=?,completed=? where app_id=?',(val,now(),aid));j=c.execute('select skills from jobs where id=?',(a['job_id'],)).fetchone();r=c.execute('select text from resumes where id=?',(a['resume_id'],)).fetchone();ev=c.execute('select * from evidence where user_id=?',(u['id'],)).fetchall();sc=score(r['text'],json.loads(j['skills']),ev,val);c.execute('update apps set match=?,trust=?,scores=? where id=?',(sc['match'],sc['trust'],json.dumps(sc),aid))
 return {'score':val,'correct':correct,'total':len(qs),'scores':sc}
@app.post('/api/applications/{aid}/feedback')
def feedback(aid:int,x:FeedbackIn,u=Depends(auth)):
 role(u,'recruiter','admin')
 if x.decision not in ('review','shortlist','interview','selected','not_selected'):raise HTTPException(400,'Invalid decision.')
 with db() as c:
  a=c.execute('select a.id,j.recruiter from apps a join jobs j on j.id=a.job_id where a.id=?',(aid,)).fetchone()
  if not a:raise HTTPException(404,'Application not found.')
  if u['role']!='admin' and a['recruiter']!=u['id']:raise HTTPException(403,'Not your application.')
  c.execute('insert into feedback(app_id,recruiter,decision,note,created) values(?,?,?,?,?) on conflict(app_id) do update set decision=excluded.decision,note=excluded.note,created=excluded.created',(aid,u['id'],x.decision,x.note[:800],now()));c.execute('update apps set status=? where id=?',(x.decision,aid))
 return {'ok':True,'message':'Decision saved for analytics; existing and future scores are not silently retrained.'}
@app.get('/api/dashboard')
def dashboard(u=Depends(auth)):
 with db() as c:
  if u['role']=='candidate':return {'resumes':c.execute('select count(*) from resumes where user_id=? and deleted=0',(u['id'],)).fetchone()[0],'applications':c.execute('select count(*) from apps where user_id=?',(u['id'],)).fetchone()[0],'evidence':c.execute('select count(*) from evidence where user_id=?',(u['id'],)).fetchone()[0]}
  if u['role']=='recruiter':return {'jobs':c.execute('select count(*) from jobs where recruiter=? and status="open"',(u['id'],)).fetchone()[0],'applicants':c.execute('select count(*) from apps a join jobs j on j.id=a.job_id where j.recruiter=?',(u['id'],)).fetchone()[0],'to_review':c.execute('select count(*) from apps a join jobs j on j.id=a.job_id where j.recruiter=? and a.status="applied"',(u['id'],)).fetchone()[0],'decisions':c.execute('select count(*) from feedback f join apps a on a.id=f.app_id join jobs j on j.id=a.job_id where j.recruiter=?',(u['id'],)).fetchone()[0]}
  return {'users':c.execute('select count(*) from users').fetchone()[0],'pending_users':c.execute("select count(*) from users where approval_status='pending'").fetchone()[0],'jobs':c.execute('select count(*) from jobs').fetchone()[0],'applications':c.execute('select count(*) from apps').fetchone()[0],'evidence':c.execute('select count(*) from evidence').fetchone()[0]}
@app.get('/api/admin/users')
def users(u=Depends(auth)):
 role(u,'admin')
 with db() as c:return [dict(x) for x in c.execute('select id,name,email,role,created,approval_status from users').fetchall()]
@app.patch('/api/admin/jobs/{jid}/approval')
def job_approval(jid:int,x:Approval,u=Depends(auth)):
 role(u,'admin')
 if x.status not in ('approved','rejected'):raise HTTPException(400,'Status must be approved or rejected.')
 with db() as c:
  exists=c.execute('select id from jobs where id=?',(jid,)).fetchone()
  if not exists:raise HTTPException(404,'Job role not found.')
  c.execute('update jobs set approval_status=? where id=?',(x.status,jid))
 return {'ok':True,'status':x.status}
@app.post('/api/admin/users')
def admin_create_user(x:AdminUserIn,u=Depends(auth)):
 role(u,'admin')
 if x.role not in ('candidate','recruiter'):raise HTTPException(400,'Choose candidate or recruiter.')
 if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',x.email):raise HTTPException(400,'Enter a valid email.')
 try:
  with db() as c:c.execute("insert into users(name,email,password,role,created,approval_status) values(?,?,?,?,?,'approved')",(x.name.strip(),x.email.strip().lower(),ph(x.password),x.role,now()))
 except sqlite3.IntegrityError:raise HTTPException(409,'Email already registered.')
 return {'ok':True,'message':f'{x.role.title()} account created and approved.'}
@app.delete('/api/admin/users/{user_id}')
def admin_delete_user(user_id:int,u=Depends(auth)):
 role(u,'admin')
 resume_files=[]
 with db() as c:
  target=c.execute('select id,role from users where id=?',(user_id,)).fetchone()
  if not target:raise HTTPException(404,'Account not found.')
  if target['role'] not in ('candidate','recruiter'):raise HTTPException(400,'Only candidate and recruiter accounts can be removed.')
  if target['role']=='candidate':
   resume_files=[r['filekey'] for r in c.execute('select filekey from resumes where user_id=? and filekey is not null',(user_id,)).fetchall()]
   app_ids=[r['id'] for r in c.execute('select id from apps where user_id=?',(user_id,)).fetchall()]
   c.executemany('delete from feedback where app_id=?',[(i,) for i in app_ids]);c.executemany('delete from tests where app_id=?',[(i,) for i in app_ids]);c.execute('delete from apps where user_id=?',(user_id,));c.execute('delete from resumes where user_id=?',(user_id,));c.execute('delete from evidence where user_id=?',(user_id,))
  else:
   job_ids=[r['id'] for r in c.execute('select id from jobs where recruiter=?',(user_id,)).fetchall()]
   app_ids=[r['id'] for r in c.execute('select id from apps where job_id in (select id from jobs where recruiter=?)',(user_id,)).fetchall()]
   c.executemany('delete from feedback where app_id=?',[(i,) for i in app_ids]);c.executemany('delete from tests where app_id=?',[(i,) for i in app_ids]);c.execute('delete from apps where job_id in (select id from jobs where recruiter=?)',(user_id,));c.execute('delete from jobs where recruiter=?',(user_id,))
  c.execute('delete from sessions where user_id=?',(user_id,));c.execute('delete from users where id=?',(user_id,))
 for key in resume_files:(FILES/key).unlink(missing_ok=True)
 return {'ok':True}
@app.patch('/api/admin/users/{user_id}/approval')
def approval(user_id:int,x:Approval,u=Depends(auth)):
 role(u,'admin')
 if x.status not in ('approved','rejected'):raise HTTPException(400,'Status must be approved or rejected.')
 with db() as c:
  target=c.execute('select id,role from users where id=?',(user_id,)).fetchone()
  if not target:raise HTTPException(404,'Account not found.')
  if target['role'] not in ('candidate','recruiter'):raise HTTPException(400,'Only candidate and recruiter accounts require approval.')
  c.execute('update users set approval_status=? where id=?',(x.status,user_id))
 return {'ok':True,'status':x.status}
@app.get('/api/admin/analytics')
def analytics(u=Depends(auth)):
 role(u,'admin')
 with db() as c:return {'roles':[dict(x) for x in c.execute('select role,count(*) count from users group by role')],'decisions':[dict(x) for x in c.execute('select decision,count(*) count from feedback group by decision')]}

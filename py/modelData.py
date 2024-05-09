from auxfuncs import *

def addTimeToDB(t0, T, db):
	""" Add relevant time indices/subsets to the database"""
	db['t'] = pd.Index(range(t0, T+1), name = 't')
	db['t0']   = db('t')[db('t')==t0]
	db['tx0']  = adj.rc_pd(db('t'), ('not', db('t0')))
	db['tE']   = db('t')[db('t')==T]
	db['t2E']  = db('t')[db('t')==T-1]
	db['txE']  = adj.rc_pd(db('t'), ('not', db('tE')))
	db['tx2E'] = db('t')[:-2]
	db['tx0E'] = adj.rc_pd(db('t'), ('not', ('or', [db('tE'), db('t0')])))
	db['tx02E']=db('t')[1:-2]


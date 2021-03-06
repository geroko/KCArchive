import os

basedir = os.path.dirname(__file__)

# Set DEBUG to false, and change BASIC_AUTH user and pass before deploying
DEBUG = True
BASIC_AUTH_USERNAME = 'admin'
BASIC_AUTH_PASSWORD = 'changeme'

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'kcarchive.db')
#SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://user:pass@localhost/kcarchive?charset=utf8mb4'
SECRET_KEY = os.urandom(16)
MEDIA_FOLDER = os.path.join(basedir, 'media')
BLACKLIST_FILE = os.path.join(basedir, 'blacklist.txt')
CACHE_TYPE = 'simple'

# Posts newer than this will not be saved, in minutes
SCRAPER_DELAY = 0

BANNER = ''

'''
Add posts to about page with syntax:
{
	'subject':'First post',
	'message':'Hello world'
}
'''
ABOUT = []

FLAG_MAP = {
	'us.png':'United States',
	'de.png':'Germany',
	'ru.png':'Russia',
	'pl.png':'Poland',
	'fi.png':'Finland',
	'ru-mow.png':'Moscow',
	'gb.png':'United Kingdom',
	'ua.png':'Ukraine',
	'proxy.png':'Proxy',
	'br.png':'Brazil',
	'au.png':'Australia',
	'se.png':'Sweden',
	'bavaria.png':'Bavaria',
	'br-south.png':'South Brazil',
	'tr.png':'Turkey',
	'nl.png':'Netherlands',
	'texas.png':'Texas',
	'ca.png':'Canada',
	'fr.png':'France',
	'mx.png':'Mexico',
	'it.png':'Italy',
	'ch.png':'Switzerland',
	'in.png':'India',
	'at.png':'Austria',
	'lv.png':'Latvia',
	'il.png':'Israel',
	'hr.png':'Croatia',
	'pt.png':'Portugal',
	'ar.png':'Argentina',
	'onion.png':'Onion',
	'lt.png':'Lithuania',
	'my.png':'Malaysia',
	'kz.png':'Khazakstan',
	'no.png':'Norway',
	'cl.png':'Chile',
	'rs.png':'Serbia',
	'es.png':'Spain',
	'by.png':'Belarus',
	'gr.png':'Greece',
	'ro.png':'Romania',
	'cz.png':'Czech Republic',
	'ee.png':'Estonia',
	'hu.png':'Hungary',
	'quebec.png':'Quebec',
	'si.png':'Slovenia',
	'ie.png':'Ireland',
	'lu.png':'Luxembourg',
	'scotland.png':'Scotland',
	'co.png':'Colombia',
	'nz.png':'New Zeeland',
	'sk.png':'Slovakia',
	've.png':'Venezuela',
	'am.png':'Armenia',
	'dk.png':'Denmark',
	'az.png':'Azerbijan',
	'kr.png':'South Korea',
	'za.png':'South Africa',
	'crimea.png':'Crimea',
	'cr.png':'Costa Rica',
	'hn.png':'Honduras',
	'ir.png':'Iran',
	'be.png':'Belgium',
	'jp.png':'Japan',
	'is.png':'Iceland',
	'ma.png':'Morocco',
	'catalonia.png':'Catalonia',
	'kw.png':'Kuwait',
	'md.png':'Moldova',
	'pe.png':'Peru',
	'id.png':'Indonesia',
	'ru-me.png':'Mari El',
	'bg.png':'Bulgaria',
	'ec.png':'Ecuador',
	'uy.png':'Uraguay',
	'ge.png':'Georgia',
	'cn.png':'China',
	'sd.png':'Sudan',
	'lk.png':'Sri Lanka',
	'al.png':'Albania',
	'ph.png':'Philippines',
	'tw.png':'Taiwan',
	'ba.png':'Bosnia',
	'pk.png':'Pakistan',
	'np.png':'Nepal',
	'iq.png':'Iraq',
	'tn.png':'Tunisia',
	'ae.png':'United Arab Emirates',
	'ps.png':'Palestine',
	'hk.png':'Hong Kong',
	'ke.png':'Kenya',
	'bd.png':'Bangladesh',
	'cy.png':'Cyprus',
	'mk.png':'Macedonia',
	'sa.png':'Saudi Arabia',
	'gt.png':'Guatemala',
	'ng.png':'Nigeria',
	'eg.png':'Egypt',
	'gh.png':'Ghana',
	'sg.png':'Singapore',
	'bj.png':'Benin',
	'ci.png':'Ivory Coast',
	'cm.png':'Camaroon',
	'dz.png':'Algeria',
	'kg.png':'Kygrzstan',
	'sv.png':'El Salvador',
	'jm.png':'Jamaica',
	'tz.png':'Tanzania',
	'tt.png':'Trinidad and Tobago',
	'zw.png':'Zimbabwe',
	'ht.png':'Haiti',
	'gu.png':'Guam',
	'ly.png':'Libya',
	'th.png':'Thailand',
	'vn.png':'Vietnam',
	'bo.png':'Bolivia',
	'do.png':'Dominican Republic',
	'ml.png':'Mali',
	'sn.png':'Senegal',
	'uz.png':'Uzbekistan',
	'jo.png':'Jordan',
	'me.png':'Montenegro',
	'mu.png':'Mauritius',
	'pa.png':'Panama',
	'sc.png':'Seychelles',
	'ye.png':'Yemen',
	'ao.png':'Angola',
	'gn.png':'Guinea',
	'lb.png':'Lebanon',
	'mg.png':'Madagascar',
	'mn.png':'Mongolia',
	'om.png':'Oman',
	'qa.png':'Qatar',
	're.png':'Réunion',
	'tg.png':'Togo',
	'ug.png':'Uganda',
	'zm.png':'Zambia',
	'kh.png':'Cambodia',
	'la.png':'Laos',
	'bh.png':'Bahrain',
	'bn.png':'Brunei',
	'bt.png':'Bhutan',
	'aw.png':'Aruba',
	'bm.png':'Bermuda',
	'cg.png':'Congo',
	'et.png':'Ethiopia',
	'ni.png':'Nicaragua',
	'mo.png':'Macao',
	'py.png':'Paraguay',
	'mm.png':'Myanmar',
	'gy.png':'Guyana',
	'mt.png':'Malta',
	'xk.png':'Kosovo',
	'vc.png':'Saint Vincent',
	'ga.png':'Gabon',
	'mr.png':'Mauritania',
	'pr.png':'Puerto Rico',
	'aq.png':'Antarctica',
	'cw.png':'Curaçao',
	'bb.png':'Barbados',
	'kp.png':'North Korea',
	'dm.png':'Dominica',
	'mc.png':'Monaco',
	'va.png':'Vatican',
	'af.png':'Afghanistan',
	'im.png':'Isle of Man',
	'bs.png':'Bahamas',
	'ls.png':'Lesotho',
	'ad.png':'Andorra',
	'td.png':'Chad',
	'ag.png':'Antigua and Barbuda',
	'so.png':'Somalia',
	'ck.png':'Cook Islands',
	'gl.png':'Greenland',
	'lr.png':'Liberia',
	'pw.png':'Palau',
	'to.png':'Tonga',
	'ai.png':'Anguilla',
	'eh.png':'Western Sahara',
	'fk.png':'Falkland Islands',
	'fm.png':'Micronesia',
	'gg.png':'Guernsey',
	'je.png':'Jersey',
	'km.png':'Comoros',
	'li.png':'Liechtenstein',
	'na.png':'Namibia',
	'pg.png':'Papua New Guinea',
	'sy.png':'Syria',
	'tm.png':'Turkmenistan',
	'tv.png':'Tuvalu',
	'yt.png':'Mayotte',
	'mp.png':'Northern Mariana Islands',
	'sm.png':'San Marino',
	'bz.png':'Belize',
	'unknown.png':'Unknown',
	'kohl.png':'Moderator'
}

MISC_FLAGS = {
	'su.png':'Soviet Union',
	'german_empire.png':'German Empire'
}

STATE_FLAGS = {
	'us-ca.png':'California',
	'us-ny.png':'New York',
	'us-tx.png':'Texas',
	'us-fl.png':'Florida',
	'us-md.png':'Maryland',
	'us-la.png':'Louisiana',
	'us-nj.png':'New Jersey',
	'us-oh.png':'Ohio',
	'us-az.png':'Arizona',
	'us-ri.png':'Rhode Island',
	'us-or.png':'Oregon',
	'us-sc.png':'South Carolina',
	'us-ok.png':'Oklahoma',
	'us-il.png':'Illinois',
	'us-ky.png':'Kentucky',
	'us-ct.png':'Connecticut',
	'us-wa.png':'Washington',
	'us-al.png':'Alabama',
	'us-co.png':'Colorado',
	'us-va.png':'Virginia',
	'us-hi.png':'Hawaii',
	'us-id.png':'Idaho',
	'us-mo.png':'Missouri',
	'us-ma.png':'Massachusetts',
	'us-nc.png':'North Carolina',
	'us-ia.png':'Iowa',
	'us-mi.png':'Michigan',
	'us-tn.png':'Tennessee',
	'us-nd.png':'North Dakota',
	'us-mn.png':'Minnesota',
	'us-wi.png':'Wisconsin',
	'us-pa.png':'Pennsylvania',
	'us-nv.png':'Nevada',
	'us-ar.png':'Arkansas',
	'us-ga.png':'Georgia',
	'us-ut.png':'Utah',
	'us-ks.png':'Kansas',
	'us-vt.png':'Vermont',
	'us-mt.png':'Montana',
	'us-me.png':'Maine',
	'us-nh.png':'New Hampshire',
	'us-in.png':'Indiana',
	'us-ak.png':'Alaska',
	'us-dc.png':'Washington DC',
	'us-de.png':'Delaware',
	'us-ms.png':'Mississippi',
	'us-ne.png':'Nebraska',
	'us-nm.png':'New Mexico',
	'us-sd.png':'South Dakota',
	'us-wv.png':'West Virginia',
	'us-wy.png':'Wyoming'
}

FRENCH_FLAGS = {
	'paris.png':'Paris'
}

FLAG_MAP = {k:v for k,v in sorted(FLAG_MAP.items(), key=lambda label: label[1])}

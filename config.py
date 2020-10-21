import os

basedir = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'kcarchive.db')}"

SECRET_KEY = os.urandom(16)

MEDIA_FOLDER = os.path.join(basedir, 'media')

BLACKLIST_FILE = os.path.join(basedir, 'blacklist.txt')

BASIC_AUTH_USERNAME = 'admin'
BASIC_AUTH_PASSWORD = 'changeme'

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
	'onion.png':'Tor',
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
	'bg.png':'Bulgaria',
	'ec.png':'Ecuador',
	'uy.png':'Uraguay',
	'ge.png':'Georgia',
	'cn.png':'China',
	'sd.png':'Sudan',
	'al.png':'Albania',
	'ph.png':'Philippines',
	'tw.png':'Taiwan',
	'ba.png':'Bosnia',
	'pk.png':'Pakistan',
	'np.png':'Nepal',
	'iq.png':'Iraq',
	'tn.png':'Tunisia',
	'kohl.png':'Moderator'
}

FLAG_MAP = {k:v for k, v in sorted(FLAG_MAP.items(), key=lambda label: label[1])}

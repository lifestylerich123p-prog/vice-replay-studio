# Builds the guide pages, /links/, sitemap.xml and robots.txt for vicereplay.com (repo vicereplay-site).
# Add a guide() call per new video, run: python tools/site_guides.py, then commit+push vicereplay-site.
import os, html, json
SITE = "/home/user/vicereplay-site"
DOMAIN = "https://vicereplay.com"
TAG = "vicereplay-20"
YT = "https://www.youtube.com/@vicereplaytv-q8s"
def amz(q): return f"{q}?tag={TAG}" if q.startswith("http") else f"https://www.amazon.com/s?k={q.replace(' ','+')}&tag={TAG}"

CSS = """:root{--bg:#0d0717;--panel:#170d26;--panel-2:#21123a;--line:#3a2357;--fg:#f4eefc;--muted:#b7a9cf;--pink:#ff1f8e;--cyan:#00e5d2;
--display:"Anton","Impact","Arial Narrow",sans-serif;--body:"Montserrat",system-ui,-apple-system,"Segoe UI",sans-serif;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--body);font-size:17px;line-height:1.65}
.wrap{max-width:720px;margin:0 auto;padding:22px max(16px,env(safe-area-inset-right,0px)) 64px max(16px,env(safe-area-inset-left,0px))}
nav{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:28px;flex-wrap:wrap}
.brand{font-family:var(--display);font-size:24px;letter-spacing:.02em;color:var(--fg);text-decoration:none}.brand b{color:var(--cyan);font-weight:400}
nav .menu{display:flex;gap:16px;font-weight:700;font-size:14px}nav .menu a{color:var(--muted);text-decoration:none}nav .menu a:hover{color:var(--pink)}
h1{font-family:var(--display);font-weight:400;font-size:clamp(32px,8vw,50px);line-height:1.15;margin:0 0 12px;text-wrap:balance}
h1 span{background:var(--pink);padding:0 .15em;-webkit-box-decoration-break:clone;box-decoration-break:clone}
h2{font-family:var(--display);font-weight:400;font-size:28px;line-height:1.15;margin:36px 0 8px;color:var(--fg)}
h2::before{content:"";display:inline-block;width:10px;height:22px;background:var(--cyan);margin-right:10px;vertical-align:-2px}
.meta{color:var(--muted);font-size:14px;margin:0 0 20px}.lede{font-size:19px;color:var(--fg)}
a{color:var(--cyan)}p{margin:0 0 14px}ul.list{padding-left:22px}ul.list li{margin-bottom:8px}
.video{position:relative;aspect-ratio:16/9;border-radius:14px;overflow:hidden;border:1px solid var(--line);margin:20px 0;background:#000}
.video iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.box{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;margin:24px 0}
.box h3{margin:0 0 10px;font-size:14px;text-transform:uppercase;letter-spacing:.1em;color:var(--cyan)}
.note{border-left:4px solid var(--pink);background:var(--panel);padding:12px 16px;border-radius:0 10px 10px 0;margin:20px 0}
.btns{display:grid;gap:8px}.item{display:grid;grid-template-columns:1fr auto;align-items:center;column-gap:12px;gap:12px;padding:14px 16px;border-radius:10px;background:var(--panel-2);color:var(--fg);text-decoration:none;font-weight:700;line-height:1.3}
.item span{color:var(--pink);font-size:20px;grid-column:2;grid-row:1/3}.item small{grid-column:1;grid-row:2;color:var(--muted);font-weight:500;font-size:13px}
.item:hover,.item:focus-visible{outline:2px solid var(--pink);outline-offset:2px}
.cards{display:grid;gap:12px}.card{display:block;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 18px;color:var(--fg);text-decoration:none}
.card:hover{border-color:var(--pink)}.card b{font-size:18px;display:block;line-height:1.3}.card small{color:var(--muted)}
.sources{font-size:14px;color:var(--muted)}.sources a{word-break:break-word}
footer{margin-top:44px;color:var(--muted);font-size:13px;border-top:1px solid var(--line);padding-top:16px}"""

def page(path, title, desc, body, wide=True):
    url = f"{DOMAIN}/{path}" if path else DOMAIN + "/"
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}"><meta property="og:site_name" content="Vice Replay"><meta name="theme-color" content="#0d0717">
<link rel="icon" href="/favicon.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@500;700;800&display=swap">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<nav><a class="brand" href="/">VICE <b>REPLAY</b></a><div class="menu"><a href="/guides/">Guides</a><a href="/gear/">Gear</a><a href="{YT}" target="_blank" rel="noopener">YouTube</a></div></nav>
<main>
{body}
</main>
<footer>Business &amp; sponsors: <a href="mailto:contact@vicereplay.com">contact@vicereplay.com</a> · <a href="/contact/">Work with us</a><br>Vice Replay is a fan channel and is not affiliated with Rockstar Games or Take-Two Interactive. Grand Theft Auto and GTA are trademarks of Take-Two Interactive. As an Amazon Associate I earn from qualifying purchases: some links on this site are affiliate links, at no extra cost to you.</footer>
</div>
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "4c4c637dcde8478da5fd7073dcde1b11"}}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>
"""
    d = os.path.join(SITE, path)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(doc)

def video(vid, title):
    return f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{vid}" title="{html.escape(title)}" loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe></div>'

def gearbox(items, intro="If you're short on space for the 212 GB install, these searches show current options and prices:"):
    lis = "".join(f'<a class="item" href="{amz(q)}" target="_blank" rel="sponsored noopener">{html.escape(label)}<span aria-hidden="true">→</span></a>' for label, q in items)
    return f'<div class="box"><h3>Gear for GTA 6 (affiliate links)</h3><p>{intro}</p><div class="btns">{lis}</div><p class="sources" style="margin:10px 0 0">Affiliate links: as an Amazon Associate I earn from qualifying purchases, at no extra cost to you. We haven\'t tested these products; check reviews and compatibility before you buy. <a href="/gear/">All gear picks</a></p></div>'

STORAGE = [("PS5 storage upgrade (2TB NVMe SSD with heatsink)", "PS5 compatible 2TB NVMe SSD with heatsink"),
           ("Xbox Series X|S storage expansion card", "Xbox Series X S storage expansion card 2TB")]
GAME = [("GTA 6 for PS5", "https://www.amazon.com/dp/B0H6K928WL"), ("GTA 6 for Xbox Series X|S", "https://www.amazon.com/dp/B0H6K49W6Y")]

def sources(lst):
    return '<div class="sources"><h2>Sources</h2><ul class="list">' + "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{html.escape(n)}</a></li>' for n, u in lst) + "</ul></div>"

def watchmore(vid):
    return f'<div class="box"><h3>Watch more</h3><div class="btns"><a class="item" href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">Watch this on YouTube<span aria-hidden="true">→</span></a><a class="item" href="{YT}?sub_confirmation=1" target="_blank" rel="noopener">Subscribe to Vice Replay<small>New GTA 6 news and Shorts every day</small><span aria-hidden="true">→</span></a></div></div>'

GUIDES = []
def guide(slug, title, desc, date, body):
    GUIDES.append((slug, title, desc, date))
    page(f"guides/{slug}/", f"{title} · Vice Replay", desc, body)

# 1. Unlock time
guide("gta-6-unlock-time", "GTA 6 Unlock Time: When You Can Play in Every Time Zone",
 "GTA 6 unlocks at midnight local time on November 19, 2026. Here's whose midnight comes first, the US question, Xbox Cloud Gaming and the New Zealand trick.",
 "2026-11-17", f"""<h1>GTA 6 unlock time: <span>whose midnight?</span></h1>
<p class="meta">Updated November 17, 2026 · Vice Replay</p>
<p class="lede">GTA 6 comes out on Thursday, November 19, 2026, on PS5 and Xbox Series X and S. It unlocks at <b>midnight local time</b> in each region, so not everyone starts at the same moment.</p>
{video("pcoMWOraJA4","GTA 6 Unlock Time in Every Time Zone")}
<h2>The rule: midnight where you are</h2>
<p>Rockstar's rule is a regional midnight unlock. Players in the furthest-east time zones get in first, and the unlock rolls west around the world over the following hours.</p>
<h2>Who plays first</h2>
<p>New Zealand reaches midnight first. According to PlayStation Store listings, that is around <b>6 AM Eastern on November 18</b>. Australia, Japan and India follow, then Europe and the UK.</p>
<h2>The US: one unlock or four?</h2>
<p>This is still debated. Some reports say US players get one shared unlock the evening of November 18, while others expect each US time zone to unlock at its own midnight. The safest way to know your exact time is your console's store page: open the GTA 6 listing and look for the release time shown there.</p>
<h2>Xbox Cloud Gaming</h2>
<p>According to Forbes, GTA 6 starts streaming on Xbox Cloud Gaming at <b>1 AM Eastern</b>, not midnight.</p>
<h2>The New Zealand trick</h2>
<p>Some players plan to switch their Xbox region to New Zealand to play early. It's unconfirmed for GTA 6 and it carries account risks. <a href="/guides/gta-6-new-zealand-trick/">Read our full breakdown of the New Zealand trick.</a></p>
<div class="note">Times change fast before a launch. Everything here is as reported two days before release; your console's store page has the final word.</div>
{gearbox(STORAGE)}
{watchmore("pcoMWOraJA4")}
{sources([("Rockstar regional release times (as cited by GTA Wiki)","https://grandtheftautowiki.com/articles/gta-6-release-time-unlock"),("Yahoo Tech: US unlock the night before","https://tech.yahoo.com/gaming/articles/gta-6-unlocks-midnight-november-124500352.html"),("Push Square: release times","https://www.pushsquare.com/guides/gta-6-release-times-when-can-you-start-playing"),("Forbes: Xbox Cloud Gaming start time","https://www.forbes.com/sites/brianmazique/2026/11/16/xbox-just-revealed-the-exact-hour-gta-6-starts-streaming-and-it-isnt-midnight/"),("Screen Rant: PS5 region purchases","https://screenrant.com/gta-6-global-launch-times-play-early/")])}""")

# 2. NZ trick
guide("gta-6-new-zealand-trick", "GTA 6 New Zealand Trick: Can You Play Early, and Is It Safe?",
 "How the GTA 6 New Zealand trick reportedly works on Xbox, why PS5 is different, and the account risks before you try it.",
 "2026-11-17", f"""<h1>The GTA 6 New Zealand trick: <span>worth the risk?</span></h1>
<p class="meta">Updated November 17, 2026 · Vice Replay</p>
<p class="lede">Some players say they can play GTA 6 up to eighteen hours early by pretending to be in New Zealand. It's unconfirmed, and it could put your account at risk. Here's what's actually reported.</p>
{video("-C9KX5Afwgw","GTA 6 New Zealand Trick")}
<h2>Why New Zealand?</h2>
<p>GTA 6 unlocks at midnight local time. According to PlayStation Store listings, New Zealand reaches that midnight first, around 6 AM Eastern on November 18. Rockstar hasn't confirmed those times.</p>
<h2>On Xbox</h2>
<p>Guides from outlets like Insider Gaming and Windows Central describe changing your Xbox's location setting to New Zealand, then switching it back later. Nobody has confirmed it works for GTA 6 yet.</p>
<h2>On PS5</h2>
<p>PlayStation is different. Reports say your store region is tied to your account, and Sony's terms reportedly rule out the shortcut. Changing the clock or the console settings won't move your unlock time.</p>
<h2>The risks</h2>
<ul class="list"><li>Fake region details can break platform rules.</li><li>Your account could get flagged.</li><li>You may need to buy the game in the New Zealand store.</li><li>Rockstar and Microsoft haven't commented.</li></ul>
<h2>Our take</h2>
<p>Not worth risking a console account for a few hours. Launch-day servers will be busy anyway. <a href="/guides/gta-6-unlock-time/">Here's when GTA 6 unlocks where you live.</a></p>
{gearbox(STORAGE)}
{watchmore("-C9KX5Afwgw")}
{sources([("Insider Gaming: Xbox NZ trick","https://insider-gaming.com/how-to-play-gta-6-early-xbox-new-zealand-trick/"),("Windows Central","https://www.windowscentral.com/gaming/xbox/grand-theft-auto-6-launch-new-zealand-changing-region"),("BGR","https://www.bgr.com/2259294/xbox-series-x-get-early-access-gta-6/"),("Digital Citizen: Sony terms and PS5","https://www.digitalcitizen.life/gta-6-ps5-new-zealand-unlock-time-psn-region-rules/"),("MP1st: unlock times","https://mp1st.com/news/gta-6-unlock-times-revealed")])}""")

# 3. Launch checklist
guide("gta-6-launch-checklist", "GTA 6 Launch Checklist: Download Size, Price and What's Missing on Day One",
 "GTA 6's install is up to 212 GB. Here's the launch-night checklist: preload, day-one patch, price, what's not there at launch, and how to dodge spoilers.",
 "2026-11-16", f"""<h1>GTA 6 launch checklist: <span>be ready at midnight</span></h1>
<p class="meta">Updated November 16, 2026 · Vice Replay</p>
<p class="lede">GTA 6 launches November 19 on PS5 and Xbox Series X and S. Here's how much space you need, what it costs, what isn't there on day one, and a simple launch-night plan.</p>
{video("vJDnv7_7Hcs","GTA 6 Launches in 3 Days")}
<h2>Download size: up to 212 GB</h2>
<p>The preload went live on November 10. Rockstar says the install is <b>up to 212 GB</b>, depending on your console, and your console may need extra temporary space while it installs. <a href="/guides/gta-6-storage/">How to make room for GTA 6.</a></p>
<h2>Price</h2>
<p>The standard edition is <b>$79.99</b> in the US and the Ultimate edition is <b>$99.99</b>. Physical copies are reportedly a code in a box, so you still need the download.</p>
<h2>Not there on day one</h2>
<ul class="list"><li><b>No PC version</b> at launch, and no PC date announced yet.</li><li><b>No GTA Online</b> for the new game on day one; it's expected sometime in 2027.</li></ul>
<h2>Your launch-night plan</h2>
<ul class="list"><li>Finish the preload early, before launch-night traffic.</li><li>On launch day, update your console and the game before midnight so the day-one patch doesn't eat your first hour.</li><li>Test your controller, headset and TV picture mode (turn on Game Mode).</li><li>Mute GTA 6 keywords on social apps: clips and spoilers will flood every feed within minutes.</li><li>Want to share your best moments? Turn on your console's capture features before you play.</li></ul>
{video("YqnShunG7WY","GTA 6 Survival Guide: 7 Things to Do Before You Play")}
{gearbox(STORAGE + GAME)}
{watchmore("vJDnv7_7Hcs")}
{sources([("Forbes: release time, download size, day-one update","https://www.forbes.com/sites/erikkain/2026/11/16/gta-6-release-date-time-ps5-xbox-series-x-download-size-day-one-update/"),("Gameluster: 212 GB preload","https://gameluster.com/gta-6-212gb-download-size-preload/"),("Rockstar Games: official GTA VI site","https://www.rockstargames.com/VI")])}""")

# 4. Map
guide("gta-6-map-leonida-places", "GTA 6 Map: 6 Places in Leonida You Need to Know",
 "GTA 6 is bigger than Vice City. A quick guide to the six places Rockstar has shown in the state of Leonida: Vice City, Leonida Keys, Grassrivers, Port Gellhorn, Ambrosia and Mount Kalaga.",
 "2026-11-13", f"""<h1>GTA 6 is bigger than <span>Vice City</span></h1>
<p class="meta">Updated November 13, 2026 · Vice Replay · No story spoilers</p>
<p class="lede">GTA 6 is set in the state of Leonida, Rockstar's take on Florida. Before launch, Rockstar showed six very different places. Here's what each one is about.</p>
{video("GjhaJdjHR4Q","GTA 6 Is Bigger Than Vice City: 6 Places to Know")}
<h2>Vice City</h2><p>The neon heart of Leonida, inspired by Miami: beaches, nightlife, money and chaos.</p>
<h2>Leonida Keys</h2><p>A chain of islands and bridges inspired by the Florida Keys: boats, sunsets and laid-back island towns.</p>
<h2>Grassrivers</h2><p>Leonida's wetlands, Rockstar's version of the Everglades: swamps, airboats and alligators.</p>
<h2>Port Gellhorn</h2><p>A fading beach-resort town on the Gulf coast, with its glory days behind it.</p>
<h2>Ambrosia</h2><p>An industrial town built around a sugar refinery, with a rough biker scene.</p>
<h2>Mount Kalaga National Park</h2><p>The wild north: forests, trails and back roads for off-road driving and hunting.</p>
<div class="note">The video uses original concept art made by us, not GTA 6 gameplay. Place descriptions are based on Rockstar's official GTA VI website.</div>
{gearbox(GAME + STORAGE, "Getting GTA 6 or making room for it? These searches show current options and prices:")}
{watchmore("GjhaJdjHR4Q")}
{sources([("Rockstar Games: official GTA VI site (places)","https://www.rockstargames.com/VI")])}""")

# 5. Storage evergreen
guide("gta-6-storage", "GTA 6 Storage Full? How to Make Room on PS5 and Xbox (212 GB)",
 "GTA 6 needs up to 212 GB. Free ways to clear space on PS5 and Xbox Series X|S first, then what to look for if you need a storage upgrade.",
 "2026-11-18", f"""<h1>GTA 6 storage full? <span>Free fixes first</span></h1>
<p class="meta">Updated November 18, 2026 · Vice Replay</p>
<p class="lede">Rockstar says GTA 6 needs <b>up to 212 GB</b>, plus some temporary space while it installs. On a base console that's a big part of the drive. Try the free fixes first; buy storage only if you still need it.</p>
<h2>Free fix 1: check what's using space</h2>
<p><b>PS5:</b> Settings → Storage → Console Storage → Games and Apps, sorted by size. <b>Xbox:</b> My games &amp; apps → Manage → Storage. Big games you finished are the first to go.</p>
<h2>Free fix 2: delete, don't lose</h2>
<p>Deleting a game doesn't delete your saves on most games with cloud saves, and you can download games you own again later. Check that cloud saves are on (PS Plus cloud storage on PS5; Xbox saves to the cloud automatically) before you delete.</p>
<h2>Free fix 3: clear captures and extras</h2>
<p>Old video clips and screenshots add up fast. So do language packs and optional modes some games let you uninstall separately.</p>
<h2>Free fix 4: park games on a USB drive</h2>
<p>Both consoles can store games on an external USB drive. PS5 and Xbox Series games need to be moved back to fast storage to play, but parking them outside is quicker than downloading again.</p>
<h2>If you still need space: the upgrade</h2>
<p><b>PS5:</b> the console has an expansion slot for an M.2 NVMe SSD (PCIe Gen4). Sony recommends a drive with a heatsink. A 2 TB drive gives you room for GTA 6 and a lot more.</p>
<p><b>Xbox Series X|S:</b> current-gen games have to run from internal storage or an official storage expansion card, which plugs into the back. A regular USB drive can store them, but can't play them.</p>
{gearbox(STORAGE + [("External USB drive (to park games)", "external hard drive for PS5 Xbox 2TB")], "These searches show current options and prices. Check compatibility with your exact console before you buy:")}
<div class="note">More GTA 6 prep: <a href="/guides/gta-6-launch-checklist/">launch checklist</a> · <a href="/guides/gta-6-unlock-time/">unlock times</a></div>
{sources([("Forbes: GTA 6 download size","https://www.forbes.com/sites/erikkain/2026/11/16/gta-6-release-date-time-ps5-xbox-series-x-download-size-day-one-update/"),("PlayStation: how to add M.2 SSD storage to PS5","https://www.playstation.com/en-us/support/hardware/ps5-install-m2-ssd/"),("Xbox: storage options for Xbox Series X|S","https://support.xbox.com/en-US/help/hardware-network/console/xbox-series-x-s-storage-options")])}""")

# 6. Cheats tracker
guide("gta-6-cheats", "GTA 6 Cheat Codes: Confirmed List (and the Fake Ones)",
 "Are there GTA 6 cheat codes? None are confirmed yet. Here's what's real, which lists are fake, and our tracker that updates when codes are verified after launch.",
 "2026-11-18", f"""<h1>GTA 6 cheat codes: <span>what's real?</span></h1>
<p class="meta">Updated November 18, 2026 · Vice Replay · We update this page when codes are verified</p>
<p class="lede">Short answer: <b>no GTA 6 cheat codes are confirmed yet.</b> Rockstar hasn't announced any, and it hasn't ruled them out. The game comes out November 19, 2026, and we'll add real codes here once they're tested.</p>
<div class="box"><h3>Confirmed GTA 6 cheats</h3><p style="margin:0"><b>None yet.</b> Check back after launch: this list gets updated as soon as codes are verified in the released game.</p></div>
<h2>Those cheat lists online are fake</h2>
<p>Most "GTA 6 cheat code" lists going around before launch are GTA 5 codes with a new name. Nobody outside Rockstar has played the final game, so nobody can have tested a code yet.</p>
<h2>Will GTA 6 have cheats?</h2>
<p>Probably. Every main GTA since GTA 3 has had cheats, typed as button combos or, in GTA 4 and GTA 5, phone numbers. But that's history, not a confirmation.</p>
<h2>What not to expect</h2>
<ul class="list"><li><b>A money cheat:</b> GTA 5 never had one, so don't count on it.</li><li><b>Cheats online:</b> GTA 5's cheats only work in story mode, and GTA Online for GTA 6 isn't expected until 2027.</li><li><b>Trophies and achievements:</b> in GTA 5, using a cheat disabled them for a while. Rockstar may do the same.</li></ul>
<h2>Scam alert</h2>
<p>Any site or video asking for your PlayStation or Xbox login, or offering a "money generator" download, is a scam. Never type your password anywhere except the official store or console.</p>
{gearbox(GAME + STORAGE, "Getting GTA 6 or making room for the 212 GB install? These searches show current options and prices:")}
{watchmore("pcoMWOraJA4")}
{sources([("GTA BOOM: current GTA 6 cheat status","https://gtaboom.com/gta-6-cheats-9nd6"),("GTA BOSS: GTA 6 cheats","https://www.gtaboss.gg/gta-6/guides/gta-6-cheats"),("GTA Wiki: Cheats in GTA VI","https://gta.fandom.com/wiki/Cheats_in_GTA_VI"),("GTAVI.tips: confirmed vs fake","https://www.gtavi.tips/gta-6-cheats")])}""")

# 7-10. News articles (Nov 17)
guide("gta-6-pc-release-date", "GTA 6 on PC: Release Date and What's Actually Reported",
 "GTA 6 launches on PS5 and Xbox Series X|S only. Here's what Take-Two has said about PC, the reported early 2027 window, and what's still unconfirmed.",
 "2026-11-17", f"""<h1>GTA 6 on PC: <span>when?</span></h1>
<p class="meta">Updated November 17, 2026 · Vice Replay</p>
<p class="lede">GTA 6 launches on November 19, 2026, on <b>PS5 and Xbox Series X|S only</b>. There is no official PC release date yet. Here's what's known and what's only reported.</p>
<h2>What's official</h2>
<p>Take-Two and Rockstar have only announced console versions. Take-Two CEO Strauss Zelnick has defended the console-first plan, saying Rockstar "always starts on console" and serves its core audience first.</p>
<h2>What's reported: early 2027</h2>
<p>According to a GamesBeat report citing four anonymous industry sources, Rockstar is reportedly aiming for a PC release between <b>January and March 2027</b>. Rockstar and Take-Two have not confirmed it. Some outlets also read Take-Two's financial outlook as a hint at early 2027, but that's an interpretation, not an announcement.</p>
<h2>History says: wait</h2>
<p>Rockstar's last big games followed the same pattern. GTA 5 reached PC about a year and a half after its console launch, and Red Dead Redemption 2 about a year after. A wait of a few months would actually be faster than usual.</p>
<h2>What PC players can do now</h2>
<ul class="list"><li>Don't buy "GTA 6 PC" keys or downloads: there's no PC version, so they're scams.</li><li>Watch Rockstar's official channels for the real announcement.</li><li>Playing on console? <a href="/guides/gta-6-storage/">Make room for the 212 GB install.</a></li></ul>
{gearbox(GAME + STORAGE, "Playing on console at launch? These searches show current options and prices:")}
{sources([("GodisaGeek: PC reportedly targets Q1 2027","https://godisageek.com/2026/10/gta-6-pc-release-date-q1-2027"),("Outlook Respawn: PC reportedly early 2027","https://respawn.outlookindia.com/gaming/gaming-news/gta-6-pc-release-reportedly-targets-early-2027"),("tbreak: Take-Two CEO on console-first","https://tbreak.com/gta-6-pc-release-delayed-console-first/"),("Gfinity: GTA 6 platforms explained","https://www.gfinityesports.com/article/will-gta-6-come-to-pc-at-launch-platforms-explained")])}""")

guide("gta-6-launch-streams", "GTA 6 Launch Streams: YouTube's 24-Hour Livestream and Kai Cenat's 100% Marathon",
 "Where to watch GTA 6 on launch night: YouTube's 24-hour livestream with 30+ creators starting November 19, plus Kai Cenat's plan to 100% the game on stream.",
 "2026-11-17", f"""<h1>GTA 6 launch night: <span>where to watch</span></h1>
<p class="meta">Updated November 17, 2026 · Vice Replay</p>
<p class="lede">GTA 6 might be the biggest launch night in streaming history. Here's what's been announced, so you know where to watch if you're not playing yet.</p>
<h2>YouTube's 24-hour GTA 6 livestream</h2>
<p>YouTube is hosting <b>"Launch Day: YouTube's 24 Hour GTAVI Livestream"</b> with more than 30 creators. According to reports, a pre-show hosted by RDCWorld starts at <b>11 PM Eastern on November 18</b>, and the 24-hour main stream begins at <b>midnight Eastern on November 19</b>, with streams in several languages.</p>
<h2>Kai Cenat's 100% marathon</h2>
<p>Kai Cenat has said he wants to complete GTA 6 to 100% on stream: not just the story, but every optional extra. How long that takes depends on how big the game really is, and nobody knows that yet.</p>
<h2>Watching without spoilers</h2>
<p>Streams will show the story live. If you want to go in blind, skip the marathons for the first few days and mute "GTA 6" on social apps. <a href="/guides/gta-6-launch-checklist/">Our launch checklist</a> has more.</p>
<div class="note">Plans can change on launch night. Check each creator's own channel for the final times.</div>
{watchmore("DIFRHVF6T0E")}
{sources([("Notebookcheck: YouTube 24-hour GTA 6 livestream","https://www.notebookcheck.net/YouTube-to-host-24-hour-GTA-6-release-date-livestream-with-launch-day-gameplay.1449040.0.html"),("GTA BOOM: 24-hour livestream with 30+ creators","https://www.gtaboom.com/gta-6-is-getting-a-24-hour-youtube-livestream-with-more-than-30-creators-5ad2"),("Streams Charts: YouTube launch marathon","https://streamscharts.com/news/youtube-announces-24-hour-gta-6-launch-marathon-global-creators"),("Sportskeeda: Kai Cenat 100% marathon","https://sportskeeda.com/us/streamers/news-kai-cenat-hold-gta-6-100-playthrough-marathon-upon-game-s-release"),("GTA BOOM: Kai Cenat wants to 100% GTA 6","https://www.gtaboom.com/kai-cenat-wants-to-100-gta-6-in-one-nonstop-marathon-d0ed")])}""")

guide("gta-6-reviews", "GTA 6 Reviews: When They Drop and the Score to Beat",
 "When do GTA 6 reviews come out? The embargo is reportedly November 18, the day before launch. Plus the Metacritic scores GTA 6 has to beat.",
 "2026-11-17", f"""<h1>GTA 6 reviews: <span>the score to beat</span></h1>
<p class="meta">Updated November 17, 2026 · Vice Replay · We'll update this when reviews are out</p>
<p class="lede">GTA 6 reviews are reportedly coming <b>November 18</b>, one day before launch. Here's what's known, and the scores Rockstar has to beat.</p>
<h2>When are reviews out?</h2>
<p>The review embargo is reportedly <b>November 18</b>. Leaker NateTheHate first pointed to that date and several outlets have repeated it, but Rockstar hasn't confirmed it. If it's right, critics' verdicts arrive the day before you can play.</p>
<h2>Early PlayStation Store ratings? Ignore them</h2>
<p>A handful of player ratings showed up on the PlayStation Store before launch. It's a tiny sample from people who can't have finished the game, so it says nothing about how good it is.</p>
<h2>The scores to beat</h2>
<ul class="list"><li><b>GTA 4:</b> 98 on Metacritic (Xbox 360)</li><li><b>GTA 3:</b> 97</li><li><b>GTA 5:</b> 97</li></ul>
<p>Anything in the high 90s puts GTA 6 with the best-reviewed games ever. Anything lower will be big news.</p>
<h2>Already in the awards race</h2>
<p>GTA 6 got <a href="/guides/gta-6-game-awards-nominations/">8 nominations at The Game Awards 2026</a>, including Game of the Year, before reviews were even out.</p>
{gearbox(GAME + STORAGE, "Buying GTA 6 or making room for it? These searches show current options and prices:")}
{sources([("Insider Gaming: GTA 6 review embargo","https://insider-gaming.com/grand-theft-auto-6-review-embargo/"),("Dot Esports: review embargo date","https://dotesports.com/gta/news/gta-6-review-embargo-date"),("Notebookcheck: PS Store reviews before embargo","https://www.notebookcheck.net/GTA-6-PS5-reviews-already-live-on-PlayStation-Store-before-embargo-and-release-date.1447176.0.html")])}""")

guide("gta-6-game-awards-nominations", "GTA 6 at The Game Awards 2026: 8 Nominations Including Game of the Year",
 "GTA 6 earned 8 nominations at The Game Awards 2026, including Game of the Year and Best Performance for Lucia's actress Manni L. Perez, two days before launch.",
 "2026-11-17", f"""<h1>GTA 6 is up for <span>Game of the Year</span></h1>
<p class="meta">Updated November 17, 2026 · Vice Replay</p>
<p class="lede">The Game Awards 2026 nominations came out on November 17, two days before GTA 6 even launched, and GTA 6 got <b>8 nominations</b>, including <b>Game of the Year</b>.</p>
<h2>Lucia's actress, confirmed</h2>
<p>One nomination finally confirmed something fans had guessed since the first trailer: <b>Manni L. Perez</b> plays Lucia. She's nominated for Best Performance. Jason's actor still hasn't been officially revealed.</p>
<h2>Why this is unusual</h2>
<p>Games have to be out by the eligibility cutoff, and GTA 6 launches November 19, just inside it. Jurors got very little time with the game before voting on nominations.</p>
<h2>When are the winners revealed?</h2>
<p>The Game Awards 2026 show is on <b>December 10, 2026</b>, at the Peacock Theater in Los Angeles.</p>
<div class="box"><h3>Watch</h3><div class="btns"><a class="item" href="https://www.youtube.com/watch?v=xvudsg_o6ow" target="_blank" rel="noopener">GTA 6 just got nominated for Game of the Year<small>Vice Replay Short</small><span aria-hidden="true">→</span></a><a class="item" href="https://www.youtube.com/watch?v=_5ZWAUY75y4" target="_blank" rel="noopener">Lucia's actress is CONFIRMED<small>Vice Replay Short</small><span aria-hidden="true">→</span></a></div></div>
{sources([("Insider Gaming: Lucia's actress revealed","https://insider-gaming.com/gta-6-lucia-actress-officially-revealed-during-2026-game-awards-nominations/"),("GamesRadar: Lucia actor revealed","https://www.gamesradar.com/games/grand-theft-auto/gta-6-lucia-actor-revealed-thanks-to-the-game-awards-best-performance-nomination-and-yes-its-exactly-who-everyone-expected/"),("Destructoid: TGA 2026 nominations","https://www.destructoid.com/gta-6-the-game-awards-tga-nominations-2026/"),("Forbes: Game of the Year nominees","https://www.forbes.com/sites/paultassi/2026/11/17/the-6-game-of-the-year-nominees-at-the-game-awards--did-gta-6-make-it/")])}""")

# guides index
GUIDES.sort(key=lambda g: g[3], reverse=True)
cards = "".join(f'<a class="card" href="/guides/{s}/"><b>{html.escape(t)}</b><small>{html.escape(d)}</small></a>' for s, t, d, _ in GUIDES)
page("guides/", "GTA 6 Guides · Vice Replay", "GTA 6 guides from Vice Replay: unlock times, download size, storage, the map and launch tips.",
     f'<h1>GTA 6 <span>guides</span></h1><p class="lede">Quick, sourced GTA 6 guides that go with our videos. No story spoilers.</p><div class="cards">{cards}</div>')

# links page
latest = GUIDES[0]
page("links/", "Vice Replay Links", "Every Vice Replay link: YouTube, TikTok, GTA 6 guides and gear.", f"""<h1>Vice Replay <span>links</span></h1>
<p class="lede">GTA's wildest moments. On replay.</p>
<div class="btns">
<a class="item" href="{YT}?sub_confirmation=1" target="_blank" rel="noopener">YouTube<small>Daily GTA 6 news and Shorts</small><span aria-hidden="true">→</span></a>
<a class="item" href="https://www.tiktok.com/@vicereplay00" target="_blank" rel="noopener">TikTok<small>@vicereplay00</small><span aria-hidden="true">→</span></a>
<a class="item" href="/guides/gta-6-cheats/">GTA 6 cheat codes<small>Confirmed list (updated after launch)</small><span aria-hidden="true">→</span></a>
<a class="item" href="/guides/">GTA 6 guides<small>Unlock times, storage, the map</small><span aria-hidden="true">→</span></a>
<a class="item" href="/gear/">GTA 6 gear picks<small>Storage, controllers, capture (affiliate)</small><span aria-hidden="true">→</span></a>
<a class="item" href="/contact/">Work with us<small>contact@vicereplay.com</small><span aria-hidden="true">→</span></a>
</div>""")

page("contact/", "Work With Vice Replay", "Sponsorships, clipping campaigns and business enquiries for Vice Replay, a GTA 6 news and Shorts channel.", f"""<h1>Work with <span>Vice Replay</span></h1>
<p class="lede">Vice Replay is a GTA 6 channel: daily news, streamer news, guides and Shorts in English, with Spanish subtitles. We post on YouTube and TikTok.</p>
<div class="box"><h3>Get in touch</h3><div class="btns"><a class="item" href="mailto:contact@vicereplay.com?subject=Vice%20Replay%20enquiry">contact@vicereplay.com<small>Sponsorships, campaigns, press</small><span aria-hidden="true">→</span></a></div></div>
<h2>What we can do</h2>
<ul class="list"><li><b>Sponsored segments</b> in a GTA 6 video or Short, clearly labeled as sponsored.</li><li><b>Clipping campaigns</b> for GTA 6 streamers and creators.</li><li><b>Gear and game features</b> on this site and in our videos.</li></ul>
<h2>What we don't do</h2>
<ul class="list"><li>Fake reviews or claims that we used a product we haven't.</li><li>Gambling, account selling, "money generators" or anything that breaks Rockstar's or YouTube's rules.</li><li>Hidden ads: every paid placement is disclosed.</li></ul>
<p>Include your brand or channel, what you have in mind, and your timing. We usually reply within 2 days.</p>""")

open(os.path.join(SITE, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
urls = [("", "2026-11-18"), ("guides/", "2026-11-18"), ("gear/", "2026-11-18"), ("links/", "2026-11-18"), ("contact/", "2026-11-18")] + [(f"guides/{s}/", d) for s, _, _, d in GUIDES]
open(os.path.join(SITE, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{DOMAIN}/{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
print("ok", len(GUIDES))

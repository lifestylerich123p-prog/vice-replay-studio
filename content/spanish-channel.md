# Vice Replay en Español: channel kit (Nov 21, 2026)

Everything to set up the Spanish channel. The owner creates it; the main chat posts to it once it's connected
(`python -m studio.youtube_es`, setup steps in `content/owner.md`).

## Name and handle
- Name: **Vice Replay en Español**
- Handle: **@ViceReplayES** (if taken: @ViceReplayEspanol, @ViceReplayEnEspanol)

## Pictures
- Profile picture: `assets/brand/profile-picture-800.png` (same as the English channel, so people recognise it)
- Banner: `assets/brand/youtube-banner-es-2560x1440.jpg` (2560 x 1440; all text inside YouTube's mobile safe area)

## Description (copy into YouTube Studio -> Customization -> Basic info)

Vice Replay en Español: noticias de GTA 6 cada mañana, en español. Streamers, récords, quizzes, el mapa de Leonida contra la vida real y los detalles que casi nadie ve. Sin spoilers de la historia.

Shorts nuevos todos los días. Suscríbete para no perderte nada de Vice City.

🌴 Guías en español: vicereplay.com/es/
🎮 Equipo para GTA 6 (Amazon): vicereplay.com/es/equipo/
📩 Contacto: vicereplay.com/contact/

Canal de fans: no afiliado a Rockstar Games ni a Take-Two Interactive. Las imágenes oficiales pertenecen a sus dueños y las usamos con comentario propio.

## Keywords (Studio -> Settings -> Channel -> Basic info)
GTA 6, GTA VI, GTA 6 español, noticias GTA 6, GTA 6 en español, Grand Theft Auto VI, Vice City, Leonida, Lucia, Jason, Rockstar Games, GTA 6 Shorts

## Settings
- Country: the owner's country of residence (it's a tax/payments field, not the audience).
- Default upload settings: category Gaming, language Spanish, "No, it's not made for kids".
- Links on the channel: vicereplay.com/es/ ("Guías en español") and vicereplay.com/es/equipo/ ("Equipo para GTA 6",
  the Spanish Amazon page; affiliate disclosure on the page).
- Playlist "GTA 6 en Español" is created automatically by the first upload.
- Channel trailer (for visitors who aren't subscribed): fLmdQepmNpw, the Bad Bunny Short (set Nov 25, 2026 by
  `python -m studio.youtube_es trailer`, which picks the most-viewed public Spanish upload).
- Branding refreshed 2026-11-25 (`python -m studio.youtube_es brand`: Spanish description for the Miami Latino
  audience, 638 characters, keywords, banner).

## Launch lineup (owner approved Nov 22: "just the best, with all the new upgrades")
Re-rendered Nov 22 with the animated captions; every one passes the views check (moving first frame, short script).
Titles in the Spanish-market style (one CAPS word + one emoji), each with a Spanish pinned question.

| When (ET) | Episode | Spanish title |
|---|---|---|
| Sun 9:30 AM | gta6-how-long-to-beat (short) | IShowSpeed terminó GTA 6 en 52 HORAS... y PERDIÓ su partida 😭 |
| Sun 12:30 PM | gta6-first-to-finish (short) | El PRIMERO en terminar GTA 6 NO fue IShowSpeed 😳 |
| Sun 3:30 PM | gta6-chapter-1-money-catch (short) | NO farmees dinero en el Capítulo 1 de GTA 6 (la trampa) 💸 |
| Mon 9:30 AM | gta6-ishowspeed-watkins (short) | IShowSpeed se EMOCIONÓ con el apellido de su familia en GTA 6 🥹 |
| Mon 12:30 PM | gta6-ultimate-edition-shops (short) | GTA 6 BLOQUEA 5 tiendas tras la edición de 100 dólares 💰 |
| Tue 9:30 AM | gta6-guess-the-ride (short) | Solo los VERDADEROS fans de GTA 6 sacan 4/4 🧠 |
| Tue 12:30 PM | gta6-map-is-florida (short) | El mapa de GTA 6 es Florida... MENOS esto 🌴 |

Left out on purpose: old renders, tips Shorts, the dog, the video store, "GTA 6 took away" (weak in English).
After launch: Spanish-streamer stories (see content/learn/ideas.md and content/learn/market-es-2026-11-22.md).

## Quota
Both channels use the same Google project, so their uploads share one daily YouTube allowance
(`python -m studio.quota`). Three Spanish uploads use about 7,500 units.

## What to make in Spanish (Nov 26)
Winners-only stays (config/channel.json `spanish_winners_only`). Spanish-only Shorts (max 1 a day): Miami/Latino
angles (Bad Bunny, Little Cuba, Vice City vs real Miami) and map "dónde está" Shorts, the only kinds that drew views in
Spanish so far (channel: 0 subscribers, 31 views in its first 11 videos as of Nov 26). Skip Spanish versions of
streamer news and plain facts.

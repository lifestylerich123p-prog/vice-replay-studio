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
📩 Contacto: vicereplay.com/contact/

Canal de fans: no afiliado a Rockstar Games ni a Take-Two Interactive. Las imágenes oficiales pertenecen a sus dueños y las usamos con comentario propio.

## Keywords (Studio -> Settings -> Channel -> Basic info)
GTA 6, GTA VI, GTA 6 español, noticias GTA 6, GTA 6 en español, Grand Theft Auto VI, Vice City, Leonida, Lucia, Jason, Rockstar Games, GTA 6 Shorts

## Settings
- Country: the owner's country of residence (it's a tax/payments field, not the audience).
- Default upload settings: category Gaming, language Spanish, "No, it's not made for kids".
- Links on the channel: vicereplay.com/es/ ("Guías en español").
- Playlist "GTA 6 en Español" is created automatically by the first upload.

## First uploads (already rendered, Spanish voice + Spanish titles)
Post 2-3 a day in the morning (9:30 AM ET = 8:30 AM Mexico City), strongest first. Each needs the owner's
"approve" like the English channel.

| Day | Short (episode, item) | Spanish title |
|---|---|---|
| 1 | gta6-how-long-to-beat, short | IShowSpeed terminó GTA 6 en 52 HORAS... y perdió su partida |
| 1 | gta6-first-to-finish, short | La primera persona en terminar GTA 6 no fue IShowSpeed |
| 1 | gta6-chapter-1-money-catch, short | No farmees dinero en el Capítulo 1 de GTA 6 (la trampa) |
| 2 | gta6-ishowspeed-watkins, short | IShowSpeed se emocionó con el apellido de su familia en GTA 6 |
| 2 | gta6-ultimate-edition-shops, short | GTA 6 bloquea 5 tiendas tras la edición de 100 dólares |
| 2 | gta6-guess-the-ride, short | Solo los fans reales de GTA 6 sacan 4/4 |
| 3 | gta6-map-is-florida, short | El mapa de GTA 6 es Florida... menos esto |
| 3 | gta6-took-away-gta5, short | GTA 6 te quitó 4 cosas que GTA 5 te daba |
| 3 | gta6-race-hud-details, short | Carreras de GTA 6: mira la esquina de la pantalla |
| 4 | gta6-black-friday-catch, short | Las ofertas de Black Friday de GTA 6 tienen trampa (before Nov 27) |
| 4 | gta6-how-long-to-beat, tips | GTA 6 tiene un MODO FÁCIL escondido (2 ajustes) |
| 4 | gta6-ranking-rides, short | GTA 6: clasifiqué 6 vehículos del gameplay de Rockstar |

Skipped: "¿Alguien ya terminó GTA 6?" (out of date), the tips and dog Shorts (the English ones flopped).
From then on, every new episode's Spanish version goes out the same day as the English one.

## Quota
Both channels use the same Google project, so their uploads share one daily YouTube allowance
(`python -m studio.quota`). Three Spanish uploads use about 7,500 units.

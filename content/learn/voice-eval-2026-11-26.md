# Voice check (es), 2026-11-26 (`python -m studio.voice_eval`)

| Voice | Words/s | Whisper word match | GTA terms heard right | Peak dBFS | Clipped % | Longest pause |
|---|---|---|---|---|---|---|
| Piper es_MX, no dictionary | 2.99 | 0.64 | 8/11 | -1.5 | 0.0 | 0.33 s |
| Piper es_MX + dictionary | 3.02 | 0.71 | 6/11 | -1.5 | 0.0 | 0.39 s |
| Kokoro em_alex + dictionary | 3.62 | 0.77 | 5/11 | -2.7 | 0.0 | 0.24 s |

Per sentence (what Whisper heard):
- **Piper es_MX, no dictionary**
  - 'Tu primera máscara en GTA 6 está en Keylento, junto a la casa de Hasson.' (match 0.77, missed: Jason)
  - 'Vise City desmiam y de verdad, ilitle Cuba es la pequeña abana.' (match 0.56)
  - 'La barbaridad más cercana es Barnacle Beaties en el sur de K -Lento.' (match 0.77)
  - 'Las guías cuentan diecinueve paí en Espray, de Caylento Apor Geyorn.' (match 0.42, missed: Port Gellhorn)
  - 'El bifot de GTA 6 aparece de noche en coton mode la que no lo pierdas.' (match 0.67, missed: Cottonmouth Lake)
- **Piper es_MX + dictionary**
  - 'Tu primera máscara en GTA 6 está en Quilento junto a la casa de Jason.' (match 0.84, missed: Key Lento)
  - 'Vice City es Miami de verdad, y Lítele Cuba es la pequeña vana.' (match 0.85)
  - 'La barbaridad más cercana es Barna Colbutis en el sur de Quilento.' (match 0.64, missed: Barnacle Beauties, Key Lento)
  - 'Las guías cuentan 19 peían spray, de Quilento Aport Keljorn.' (match 0.43, missed: Pay 'n' Spray, Port Gellhorn)
  - 'El bifot de GTA 6 aparece de noche en Cotonous Lake, no lo pierdas.' (match 0.79)
- **Kokoro em_alex + dictionary**
  - 'Tu primera máscara en GTA 6 está en Quilento, junto a la Casa de Jason.' (match 0.84, missed: Key Lento)
  - 'By City es Miami de verdad y little cuba es la pequeña abana.' (match 0.85, missed: Vice City)
  - 'La barbaría más cercana es Barna Colbutis en el sur de Quilento.' (match 0.64, missed: Barnacle Beauties, Key Lento)
  - 'Las guías cuentan 19 Pian spray de Quilento a Port Gellhorn.' (match 0.67, missed: Pay 'n' Spray)
  - 'El Big Ford de GTA 6 aparece de noche en Cottonmouth Lake, no lo pierdas.' (match 0.83, missed: Bigfoot)

Not measured here (needs a listener or real data): emotional expression, comedic timing, how natural the accent sounds to Latin American / Spanish / US Latino viewers, and retention (compare % watched by voice once the Spanish channel's Analytics are pulled). Natural pace for Spanish Shorts narration is roughly 2.5-3.2 words/s; clipping should stay at 0% with peaks under -1 dBFS.

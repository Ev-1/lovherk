
# Hvordan bruke lovherket


##### Hvordan lese "help" meldinger:

- <argument> betyr at argumentet er obligatorisk
- [argument] betyr at argumentet er valgfritt
- [argument=default] betyr at argumentet er valgfritt, men vil bli "default" om du ikke skriver inn noe.

Ikke ta med <> eller [] som en del av kommandoene.

#### Obs! 
Alle kommandoene her er skrevet uten en prefiks siden den kan endres. Så f.eks. `lovset fjern <lov>` vil kunne se ut som `§lovset fjern <lov>` eller `!lovset fjern <lov>` avhengig av hvilke(n) prefiks(er) som er valgt.

Jeg beklager for dårlig blanding av norsk og engelsk.😐

# Vise regler

- `lov [lov] [num]`
  - Viser valgte regler.

`[lov]` er her det settet med regler man vil vise.

`[num]` er de reglene fra det valgte settet man vil vise. Er num ikke oppgitt så vil alle reglene vises. [num] en liste med tall separert av mellomrom.

Om et standard regelsett er satt(se `lovset default`), så vil det gå an å la være å skrive inn `[lov]`.

Eksempler
- `lov #kanal`
  - viser alle reglene som er satt opp for #kanal
- `lov #kanal 2`
  - viser regel 2 i regelsettet som heter #kanal.
- `lov #kanal 2 5 6`
  - viser regel 2, 5 og 6 i regelsettet som heter #kanal.

Hvis default er satt til et sett ved navn `grunnregler` vil `lov grunnregler 1 3` og `lov 1 3` gi samme resultat. Merk at dette gjelder bare om man oppgir spesifikke regler. `lov` vil fortsatt vise alle regelsettene i lovherket og `lov grunnregler` vil vise alle reglene i `regler` 


# Regler
![regler](https://i.imgur.com/AESg9Yq.png)

Man kan endre på reglene i lovherket med `§lovset` kommandoen.

- `lovset ny <lov> [newrule]`
  - Lager et nytt sett med regler med navnet gitt i `<lov>`. `[newrule]` er frivillig siden hva reglene skal inneholde kan endres på med lovset oppdater.

- `lovset oppdater <lov> [newrule]`
  - Oppdaterer teksten til et sett med regler. Her er `<lov>` navnet på reglene og `<newrule>` det reglene skal endres til.

- `lovset fjern <lov>`
  - Fjerner reglene med navn `<lov>`.

- `lovset plaintext <lov>`
  - Sender reglene i en kodeblokk sånn at de kan kopieres med formatering.

- `lovset default <lov>`
  - Setter et sett med regler til å være "standardsettet". Det gjør at om "grunnregler" settes til å være standard så vil `lov grunnregler 4` og `lov 4` gi samme svar.


Hvis man lager et sett med regler og vil at man skal kunne henvise til enkeltregler må enkeltreglene være på følgende format:

`§ n: regel`

og være på en egen linje. Her er n er nummeret til regelen. Eks.

`§  4: Hold deg til riktig kanal.`



### Autoopdatering
![regler](https://i.imgur.com/OKuZxD3.png)

Bruk `§autoset` kommandoen for å styre hvilke meldinger som skal oppdateres automatisk når reglene endres.

- `autoset add <lov> <link>`
  - Gjør at meldingen som er lenket til oppdateres automatisk. Da skal oppdateres om reglene med navn `<lov>` oppdateres. Nyttig for dette for festa(pinned) meldinger.

- `autoset fjern <link>`
  - Gjør det motsatte av `add`, gjør at meldingen lenket til ikke lenger oppdateres automatisk.

- `autoset liste`
  - Gir en liste over meldinger på serveren som er satt til å oppdateres automatisk.

- `autoset fiks`
  - Får Lovherket til å forsøke å oppdatere alle meldingene som har blitt satt til oppdatering.

- `autoset post <lov>`
  - Får lovherket til å sende en melding med reglene i `<lov>` som automatisk blir satt til å oppdateres. Nye meldinger sendes som embed.

- `autoset format <link> <embed|text>`
  - Endrer en melding som allerede oppdateres automatisk mellom embed og vanlig tekst. `embed` viser reglene i en embed-boks, `text` viser dem som vanlig tekst. Nyttig for å rydde i eldre meldinger som har drevet ut av synk.



### Reaksjonsregler
![regler](https://i.imgur.com/KFlrLv9.png)

Bruk `§reactset` kommandoen for å styre hvilke meldinger som har en "alternativ" versjon(Oversettelse til engelsk) og hvilke meldinger som skal ha en emoji(📨) man kan trykke på for å tilsendt disse reglene.

Disse reglene er bare andre versjoner av regler som allerede finnes i lovherket, man kan derfor ikke ha noen regler som er eksklusivt reaksjonsregler. Derfor er det heller ikke en "ny"-kommando, bare en for å oppdatere og en for å fjerne.

Siden disse reglene skal være andre versjoner av de vanlige er de heller ikke tilgjengelige med den vanlige `lov` kommandoen, men `reactset vis` må brukes.

- `reactset oppdater <lov> <newrule>`
  - Funker som `lovset oppdater` men endrer på reaksjonsreglene.

- `reactset fjern <lov>`
  - Fjerner de alternative reglene for `<lov>` og reaksjonene som sender dem.

- `reactset link <lov> <link>`
  - Fungerer som `autoset add`. Kobler sammen en melding og en reaksjon som sender `<lov>` sine alternative regler.

- `reactset unlink <link>`
  - Fjerner koblingen mellom en melding og en reaksjon, fjerner også reaksjonen om Lovherket har tilgang til meldingen.

- `reactset liste`
  - Gir en liste over hvilke meldinger som er satt opp til å fungere som reaksjonsregler. Fungerer likt som `autoset liste`

- `reactset vis <lov>`
  - Brukes for å vise de alternative reglene i lovherket. De vil sendes som "plaintext" sånn som `lovset plaintext` gjør.


### Andre kommandoer

- `kanal #kanal`
  - Ber brukere gå til #kanal.

- `uptime`
  - Viser hvor lenge botten har vært oppe.

- `lockdown [enable=på]`
  - gjør at alle kanaler får 2 minutters slowmode. Å skrive ingenting eller på skrur på lockdown. Alle andre argumenter skrur av. I tilfelle det blir masse spam.

- `saktemodus [enable=på] [seconds=30]`
  - Denne ser litt forvirrende ut om du bruker `§help`, men det er for at den skal være enkel å bruke. Se eksempler på bruk nederst 



#### Forklaring av saktemodus.

For å skru på kan man bruke:

- `saktemodus` og `saktemodus på`
  - gir 30 sekunders slowmode
- `saktemodus <sek>` og `saktemodus på <sek>`
  - gir slowmode på `<sek>` sekunder

For å skru av kan man bruke:

`saktemodus av`, `saktemodus 0` og `saktemodus på 0`
# AI-SQ Universal Root-Inquiry / Universelle Radikalnachforschung

<p align="center">
  <a href="README.md">简体中文</a> ·
  <a href="README.en.md">English</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.fr.md">Français</a> ·
  <b>Deutsch</b>
</p>

> **Kern in einem Satz**
> **Radikalnachforschung = Fragenbaum × Evidenzkette × Lückenrekursion × Faktorenraum × Geltungsbereich und Gegenbeispiele × Ebenenprüfung × Abdeckungssättigung × Abbruchkontrolle × strukturierter Bericht.**

Version **2.4.0** · Deutsch (de) · MIT · Reiner Text, keine Laufzeitabhängigkeiten

---

## Zuerst: was es nicht ist

v2.0 behauptete, es gelte „für alle Bereiche“. Dieser Satz verletzte das fünfte Prinzip des Skills selbst — **sobald das Wort „alle“ fällt, ist man verpflichtet, nach Gegenbeispielen zu suchen**. Die Gegenbeispiele lagen sofort vor, also zog v2.1 die Behauptung zurück und ersetzte sie durch eine ehrliche Bilanz:

| Eignung | Bereiche | Warum |
|---|---|---|
| **Stark** | Wissenschaftliche Mechanismen, Technologieauswahl, historische Quellen | Schlussfolgerungen ruhen auf der Primärebene, und **der Falsifikationsweg ist offen** (Replikation, Quellcode + Messung, Quellenkritik) |
| **Mittel** | Recht, Finanzen/Wirtschaft, Politik | Stark bei Gesetzestexten, Offenlegungen und Dokumentenrecherche; schwach bei fallspezifischen Fakten, internen Daten und Kontrafaktischem |
| **Schwach** | Klinische Entscheidungen, Fehler in privaten Systemen, Mehrparteienspiele | Die Entscheidungsvariablen sind private Daten dieses Individuums oder dieser Lage; Recherche erreicht sie nicht |
| **Nicht geeignet** | Mathematischer Beweis, ästhetisches Urteil, Echtzeitentscheidungen, nicht offengelegte Daten | Deduktive Probleme, keine falsifizierbare Aussage, Zeitbudget zu knapp, Evidenz außerhalb des öffentlichen Bereichs |

Vollständige Kriterien, der „irreführendste Punkt“ je Bereich und Degradationspfade in [`references/domain_fit.md`](ai-sq-universal/references/domain_fit.md).

---

## Was es garantiert — und was nicht

**Garantiert**: Schlussfolgerungen sind nachvollziehbar (ID + wörtlicher Satz + Grad); der Geltungsbereich wird geprüft (für wen gilt es, wann nicht); **Faktoren werden enumeriert** (nicht „eine Kette gegraben und abgegeben“); der Abbruch hat einen Grund (es unterscheidet „fertig“ von „komme nicht weiter“).

**Garantiert nicht**: umsetzbare fachliche Entscheidungen; Primärdaten; deduktive Schlüsse; Antworten in Sekunden.

---

## Kern: warum drei Abdeckungsmechanismen

v2.0 hatte nur die neunschichtige Fragetkette — ein **Vertikalschnitt**: ein Objekt an einem einzigen Fragefaden nach unten graben. Reale Probleme bestehen aber meist aus „vielen Faktoren, die zusammenwirken“. Ein Vertikalschnitt kann nach drei Ketten enden, während sechs weitere Faktorenklassen nie gedacht wurden.

**Tiefe ≠ Abdeckung.** Der Vertikalschnitt hat zudem einen subtileren blinden Fleck: Er weiß nicht, „was der Kunde fragen wird“. Daher übernimmt jeder Mechanismus eine Schicht:

```
Vertikal:  neunschichtige Kette ──────→ tief (eine Linie bis zum Grund)
Flächen:   14-Dimensionen-Raster (D1–D14) → vollständig (die Flächen, die Entscheider fragen)
Querschnitt: Faktorenraum (9 Achsen + Größenordnung) → fein (keine ganze Faktorenklasse übersehen)
Schichten: Schichtungsmatrix ─────────→ präzise (derselbe Faktor kehrt sich je nach Kontext um)
Gelenke:   Interaktion und Confounding (15 Muster) → real (Faktoren sind nicht unabhängig)
Abnahme:   Abdeckungssättigung (6 Kriterien) → prüfbar („umfassend“ hört auf, Adjektiv zu sein)
Zitat:     Zitat auf Satzebene (Fundstelle + wörtlich) → nachprüfbar (jede Aussage in 30 Sekunden prüfbar)
```

### 1. Komplexitätsstufen L1–L4: erst die Stufe festlegen, dann den Umfang

| Stufe | Strukturelles Kriterium | Pflichtprüfungen |
|---|---|---|
| **L1 Einzelkette** | Eine dominante Ursache → eine Hauptwirkung, und Schichtungs-/Interaktionsprüfung fand keine Vorzeichenumkehr | Neunschichtige Kette + Gegenbeispiele; kein Faktorenraum |
| **L2 Multifaktoriell** | ≥3 relativ unabhängige Faktoren, keine Vorzeichenumkehr | Faktorenraum + Größenordnung + Vorabprüfung auf Kollinearität/Confounding |
| **L3 Interaktion/Heterogenität** | Vorzeichenumkehr nach Schichtung, nicht-additive Gemeinsamwirkungen, Schwellen/Nichtlinearität, unterschiedliche Mechanismen zwischen Fällen | L2 + Interaktionsmatrix + Schichtungsmatrix |
| **L4 Dynamisches System** | Bidirektionale Kanten im Kausalgraphen, bidirektionale Zeitbelege, bekannte Verzögerungen, Regimewechsel | L3 + Kausalgraph + Verzögerungen + Szenarioanalyse + drei Felder zu Modellgrenzen |

Von den fünf harten Regeln zählen zwei am meisten:

- **Stufe ist orthogonal zur Faktorenzahl**: viele Faktoren, aber alle linear = L2; wenige Faktoren, aber starke Rückkopplung = L4. „Viele Faktoren“ nicht mit „komplex“ verwechseln.
- **Stufe ≠ Vollständigkeit**: Die Stufe bestimmt, „welche Prüfungen Pflicht sind“; das Budget bestimmt, „wie viele diesmal erledigt werden“. Bei knappem Budget wird die Stufe **nicht gesenkt**: Unerledigtes wird als `unchecked` markiert. Eine Stufensenkung verwandelt „nicht geprüft“ stillschweigend in „musste nicht geprüft werden“.

Eine weitere Regel gegen Selbsttäuschung: **„keine Vorzeichenumkehr gefunden“ ist nicht „es gibt keine Vorzeichenumkehr“**. Ohne Schichtungs-/Interaktionsprüfung hat man kein Recht, L1/L2 zu vergeben — eine Stufe höher behandeln und in `gaps` dokumentieren.

### 2. Faktorenraum: achsenweise enumerieren, nie aus dem Gedächtnis

Alle neun Achsen mechanisch durchgehen. Jede Achse hat entweder Faktoren oder vermerkt „leer, Begründung“. Eine Lücke und eine bestätigte Abwesenheit sind zwei verschiedene Dinge.

| Achse | Was am häufigsten fehlt |
|---|---|
| Zeit | Querschnittsdaten als kausal behandelt; Verzögerungen unsichtbar |
| Raum/Ebene | Ökologischer Fehlschluss (Gruppenschluss auf Individuen angewandt) |
| Akteur | Nur objektive Faktoren zählen, „wer entscheidet“ auslassen |
| Materie/Ressourcen | Ressourcenbeschränkung als „alles andere gleich“ behandeln |
| Regeln/Institutionen | Institutionellen Wandel ignorieren, der Effekte umkehrt |
| Information/Kognition | Einen vollinformierten, rationalen Akteur annehmen |
| Technik/Werkzeuge | Generationenunterschiede der Technik ignorieren |
| Umwelt/externe Schocks | Einmaligen Schock als strukturelle Ursache schreiben |
| Rückkopplung/Dynamik | Statische Rahmen sehen keine Dynamik |

Jeder Faktor muss `role` (notwendig/fördernd/Schwelle/modifizierend/Confounder), `direction`, **`magnitude`**, `magnitude_basis`, `proxy` und `how_to_test` tragen.

**Größenordnung ist Pflicht**: `dominant` / `major` / `minor` / `unknown` (unknown muss begründet werden). Verboten: „Alle genannten Faktoren sind wichtig und müssen zusammen betrachtet werden“ — dieser Satz hat null Informationsgehalt.

### 3. Interaktion und Confounding: 15 aktiv zu vergleichende Muster

Siehe [`references/complexity_patterns.md`](ai-sq-universal/references/complexity_patterns.md): Confounding, Mediation, Effektmodifikation, Interaktion, Kollider, Simpson-Paradox, ökologischer Fehlschluss, Schwelle, Rückkopplung, Verzögerung, Pfadabhängigkeit, Äquifinalität, Proxy-Fehler, Selektionsbias, Phasenübergang. Jeder Eintrag enthält „wie erkennen / was fragen / Suchhinweise / häufige Fehlurteile“.

Die Ausgabe muss `checked-none` enthalten — **sonst kann der Leser „geprüft, nichts gefunden“ nicht von „nie geprüft“ unterscheiden**.

### 4. Abdeckungssättigung: „umfassend“ prüfbar machen

Sechs Kriterien in Bericht §14; fehlt eines, darf man nicht sagen „systematisch abgedeckt“:

1. **Achsenabdeckung**: alle 9 Achsen durchlaufen, leere Achsen begründet
2. **Größenordnungsabdeckung**: jeder Faktor hat eine Größenordnung; unknown hat einen Grund
3. **Sättigung**: zwei aufeinanderfolgende Runden ohne neue Faktoren und Achsen
4. **Negativraum**: Faktoren auflisten, die „dem gesunden Menschenverstand nach existieren müssten, aber nicht gefunden wurden“ ← **die größten Lücken liegen meist hier**
5. **Interaktionsprüfung**: Paare von dominant/major-Faktoren geprüft
6. **Schichtungsprüfung**: ob ≥2 Schlüsselschichten sich umkehren

### 5. Dimensionenraster: 14 Frageflächen (die dritte Abdeckung)

Die ersten beiden Mechanismen regeln „wie tief eine Frage reicht“ und „welche Faktorentypen ein Ergebnis hat“. Keiner regelt „**welche Flächen diese Untersuchung beantworten soll**“. Der Investor fragt nach dem Markt, der Ingenieur nach Leistungsreserven, der Einkauf nach TCO, die Rechtsabteilung nach Compliance-Grenzen — fehlt eine, ist der Bericht für eine Lesergruppe unvollständig.

| # | Dimension | # | Dimension |
|---|---|---|---|
| D1 | Ziel und Entscheidungskontext | D8 | Politik, Regulierung, Normen |
| D2 | Definitionen, Grenzen, Konventionen | D9 | Akteure, Anreize, Beschaffungskette |
| D3 | Leistung und technische Fähigkeit | D10 | Zeit, Phasen, Roadmap |
| D4 | Wirtschaftlichkeit (TCO) | D11 | Risiko, Fehlermodi, Gegenbeispiele |
| D5 | Markt und Nachfrage | D12 | Evidenzqualität und Kontroversen |
| D6 | Wettbewerb und Peers | D13 | Entscheidungsimplikationen und Alternativen |
| D7 | Lieferkette, Kapazität, Lieferung | D14 | Offene Fragen, Negativraum, nächste Schritte |

Jede Dimension liefert: Pflichtfragen / benötigtes Material / **typische Schwierigkeiten (hier wachsen die Äste)** / Mindestevidenz / wann unknown gilt. Pflichtdimensionen nach Objekttyp aktivieren; **jede nicht aktivierte Dimension muss „warum nicht gewählt“ angeben**.

**Vier Runden Lückensuche**: R1 Dimensionsebene → R2 Faktorenebene → R3 Gegenbeispielsebene (mit eigenem Durchgang zu Aussteigern und Fehlschlägen) → R4 Negativraumebene. Sättigung erst nach zwei Runden ohne Zuwachs.

Siehe [`references/dimension_outline.md`](ai-sq-universal/references/dimension_outline.md).

### 6. Zitat auf Satzebene: die kleinste prüfbare Evidenzeinheit

„Hat eine Quelle“ genügt nicht. Der evidenzähnlichste und unzuverlässigste Teil eines Berichts ist die Literaturliste — **ein erfundenes Zitat liest sich genau wie ein echtes; der einzige Unterschied ist, dass es sich nicht lokalisieren lässt**.

Jede Kernaussage muss liefern: **Fundstelle** (Seite/Absatz/Klausel/Tabellenzeile/Zeitstempel) + **wörtlicher Satz** + Kontext + Quelleninstanz und Veröffentlichungsdatum + Rückverfolgungskette.

Vier harte Regeln:

1. **Muss bis zum Satz reichen**: ein bloßer Link, ein Berichtstitel oder „irgendein WeChat-Konto“ sind automatisch unzulässig.
2. **Sekundärquellen werden nach dem schwächsten Glied bewertet**: ein WeChat-Konto, das eine Studie nacherzählt = als WeChat-Konto C/D, und **der Rückgriff auf die Primärquelle muss versucht werden**.
3. **WeChat-Konten sind nur Hinweise**; Behörden­dokumente müssen **Dokumentnummer + Klauselnummer + Inkrafttreten** angeben (und auf aktuelle Gültigkeit geprüft werden).
4. **Kontext verhindert Abschneiden**: dass das Original eine Verneinung ist, ein zur Widerlegung angeführtes Beispiel oder die Ansicht Dritter — diese drei sind die häufigsten Wege, etwas als sein Gegenteil zu zitieren.

Quellen ohne „Satz“: Datenbanken werden über „Datenbank + Feld + Zeitraum + Konvention“ lokalisiert; Interviews/interne Dokumente werden als `unverified` markiert und gehen nicht in Kernaussagen ein; Paywalls zitieren nur tatsächlich gelesene Seiten.

Siehe [`schemas/citation.json`](ai-sq-universal/schemas/citation.json) und [`prompts/citation_auditor.md`](ai-sq-universal/prompts/citation_auditor.md).

---

## Repository-Struktur

```text
AI-SQ-Universal-Root-Inquiry/
├── README.md                  Diese Datei (Chinesisch)
├── README.{en,ja,ko,es,fr,de}.md  Übersetzungen
├── INSTALL.md                 Installation / Prüfung / Fehlersuche / Deinstallation
├── CHANGELOG.md    VERSION    LICENSE
├── ai-sq-universal/           ← Der Skill selbst (kann direkt nach ~/.dsh/skills/)
│   ├── SKILL.md               Hauptspezifikation: vertikal+horizontal, Stufen, Sättigung, Qualitätsgate
│   ├── prompts/               9 Ausführungs-Prompts
│   ├── schemas/               6 Verträge
│   ├── references/            5 Referenzspezifikationen
│   ├── domain_packs/          7 Domänenpakete + Adapterhinweise
│   ├── templates/report.md    §0 + vierzehn Abschnitte (§1–§14) Berichtsvorlage
│   ├── evals/cases.yaml       13 domänenübergreifende Fälle
│   ├── examples/              5 Beispiele
│   └── scripts/               validate.py  quality_gate.py  build_docx.py
├── docs/                      ← GitHub-Pages-Landingpage (Chinesisch)
├── plugin/                    Manifest + Cordis-Patch + plattformübergreifende Installer
└── tools/build_release.py     Reproduzierbares Packaging
```

---

## Schnellstart

```powershell
cd plugin
.\install.ps1                 # Windows, Copy-Modus, keine Konfigurationsänderung
```

```bash
cd plugin && ./install.sh     # macOS / Linux
```

Dann einfach den Bedarf nennen:

> Radikalnachforschung zur Pathogenität von O157:H7: **welche Faktoren wirken**, wie stark jeder einzelne, und sind alle Stämme pathogen?

> Dieselbe Umweltauflage: Warum verbesserte sich Provinz A deutlich, während B fast keine Wirkung zeigte? Zerlege die Faktoren und ihre Interaktionen.

> Grabe diesen Klauselkonflikt aus: Welche gilt, allgemeines oder spezielles Recht, und gibt es Ausnahmen?

Quantorenfragen werden zuerst disambiguiert („wie viele Absätze hat dieser Vertrag“).

Selbstprüfung:

```bash
python ai-sq-universal/scripts/validate.py
```

---

## Ablauf (dreizehn Schritte)

```
INIT → BRIEF → AMBIGUITY_CHECK → SCOPE → COMPLEXITY → PLAN → RETRIEVE → EXTRACT
     → VERIFY → ANSWER_NODE → EXPAND_GAPS → FACTOR_SPACE → STOP_CHECK → NARRATE → REPORT
```

| Schritt | Was er verhindert |
|---|---|
| INIT | Falsches Ziel |
| **BRIEF** | **Präzise, aber nutzlos: niemand kann danach handeln** (fünf Zweckfragen + fünf Anspruchsgruppen) |
| AMBIGUITY_CHECK | „Wie viele Absätze“ auf der falschen Dimension beantworten |
| **SCOPE** | **Nur das Gefragte beantworten und die erfolgsentscheidenden Variablen auslassen** (Scope-Erweiterungsaudit) |
| **COMPLEXITY** | Einfache Fragen überdehnen / komplexe Fragen oberflächlich abfertigen |
| PLAN | Vage Fragen |
| RETRIEVE | Eine Enzyklopädie als Schlussfolgerung nehmen |
| EXTRACT | Aussagestärke stillschweigend aufblähen (`quote` muss wörtlich sein) |
| VERIFY | Kategorien auf Einzelfälle anwenden; Korrelation als Kausalität |
| EXPAND_GAPS | Endloses Nachfragen (eine Frage pro Lücke, ≤5, dedupliziert) |
| **FACTOR_SPACE** | **Nach einer einzigen Kette abgeben** |
| **STOP_CHECK** | „Nicht fertig“ als „fertig“ tarnen |
| **NARRATE** | Abschnitte, die mit „die folgende Tabelle zeigt …“ beginnen, sodass niemand die Aussage kennt |
| REPORT | Nicht nachprüfbar |

---

## Evidenzgrade (harte Vorgabe)

| Grad | Bedeutung | Verwendung |
|---|---|---|
| **A** | Autoritative Datenbanken/Normen/Regulierung/Leitlinien/amtliche Statistik + hochwertige systematische Reviews, mehrere Quellen übereinstimmend | Trägt Kernaussagen |
| **B** | Peer-reviewte Primärforschung, Berichte autoritativer Institutionen | Trägt Aussagen |
| **C** | Preprints, Branchenberichte, Einzelstudien, automatische Annotation | **Nur Hinweise** |
| **D** | Enzyklopädien, Nachrichten, ungeprüfte Webseiten | **Nie für Kernaussagen** |

Domänenpakete dürfen Grade **verfeinern**, nicht pauschal herabstufen. Ohne ID: Herabstufung plus Markierung `id_missing` — eine erfundene ID ist schlimmer als keine.

---

## Abbruchregeln

Auf Knotenebene neun Bedingungen (Evidenzschluss / zwei Runden ohne neue Information / geringer Grenznutzen / Budget / nur noch C–D übrig / unauflösbarer Konflikt / hohes Risiko erfordert Prüfung / außerhalb des Rechercheumfangs / Ambiguität ungelöst).
Global: alle hochpriorisierten Knoten geschlossen **und** die sechs Abdeckungskriterien erfüllt, oder Budget erschöpft mit dokumentierten Lücken.

**Jeder Abbruch schreibt einen `stop_reason`.**

---

## Bericht: §0 + vierzehn Abschnitte (§1–§14), Lieferung als Word

Geschrieben wird in Markdown (Modelle ändern es leicht); **geliefert wird Word** (Leser müssen es öffnen). `scripts/build_docx.py` erzeugt aus demselben Markdown ein docx: Deckblatt, Inhaltsverzeichnis, Kopf-/Fußzeile, gestreifte Tabellen, klickbare Zitate; dazu JSON für maschinelle Prüfungen. **Nie manuell als Word speichern** — das ist die Wurzel der Entfremdung zwischen Dokument und Aussagen. Seit v2.4 beginnt der Bericht mit **§0 Zweck und Anspruchsgruppen** und ergänzt §14 Abdeckungs- und Sättigungserklärung — ohne sie ist „umfassend“ nur ein Adjektiv.

Vorlage in `templates/report.md`; ausgefülltes Beispiel in [`examples/01-bacteriology.md`](ai-sq-universal/examples/01-bacteriology.md) (mit Faktorenraum-Tabelle und ehrlicher Erklärung „Abdeckung unvollständig“).

---

## Qualitätsgate

```bash
python ai-sq-universal/scripts/quality_gate.py report.md --json report.json --complexity 3 --risk high
```

Die Prüfungen skalieren mit der Komplexität: L2 prüft Faktoren und Größenordnungen; L3 prüft Interaktionen/Schichten/`checked-none`; L4 prüft Rückkopplung und Modellgrenzen. Zusätzlich geprüft: alle vierzehn Abschnitte, Nachvollziehbarkeitsrate, **analysierbare Zitatfundstellen**, **Spalte wörtlicher Sätze**, **Abfangen vager Zuschreibungen**, **Medien dürfen nicht A/B erhalten**, Stichprobenprüfungen, absolute Formulierungen, Abbruchgründe, Haftungsausschlüsse, Negativraum. Ausgabe PASS/FAIL mit Exit-Code, CI-tauglich.

---

## Evaluation

13 Fälle aus Wissenschaft, Recht, Finanzen, Geschichte, Technik, Politik, Wirtschaft, mehrdeutigen Objekten, unbeantwortbaren Fragen und Hochrisikofragen — darunter **zwei schwierige L3-Multifaktor-Fälle** (gleiche Politik, gegensätzliche Ergebnisse in zwei Regionen; gleicher Stamm, unterschiedliche Ausgänge) und ein **schwieriger Fall zum Zitat auf Satzebene** (eine Sekundärzahl eines WeChat-Kontos prüfen und zur Primärquelle zurückverfolgen). Jeder Fall trägt `probes` / `must_show` / `must_not` / `expected_stop` / `complexity`; jeder `must_not`-Treffer ergibt null.

---

## Designprinzipien (zwölf)

1. Domänenunabhängiger Kern + Domänenadapter — der Kern kodiert keine Domänenterminologie
2. **Erst die Komplexitätsstufe festlegen, dann die Tiefe** — verhindert Schablonen und Flüchtigkeit
3. **Vertikal für Tiefe, horizontal für Abdeckung** — neunschichtige Kette + Faktorenraum, beides nötig
4. Lückengesteuert — nur Informationslücken verfolgen, keine Frage wiederholen
5. Evidenz zuerst — Kernaussagen brauchen Quelle, wörtlichen Satz, ID, Grad
6. Bereichsbegrenzung — global/Klasse/Instanz/Bedingung/Zeit/Geografie
7. Gegenbeispielprüfung — bei „alle/jeder/immer/einzig“ Gegenbeispiele suchen
8. Ebenenprüfung — Träger nicht als Element, Produkt nicht als Ursache, Kategorieeigenschaft nicht als Instanzeigenschaft behandeln
9. Erst disambiguieren — klären oder Annahmen erklären
10. **Abdeckung prüfbar** — sechs Kriterien; fehlt eines, „Abdeckung unvollständig“ sagen
11. Menschliche Prüfung bei hohem Risiko — Medizin/Recht/Finanzen/Sicherheit/Politik/Psychologie
12. Doppelte Ausgabe — JSON + Markdown

---

## Fehlermodi und Gegenmaßnahmen

| Fehlermodus | Gegenmaßnahme |
|---|---|
| Endloses Nachfragen | Budget + Dedup-Schlüssel + Grenznutzen-Abbruch |
| **Nur eine Kette graben** | Komplexitätsstufen + Faktorenraum + Achsenenumerierung |
| **Undifferenzierte Faktorenliste** | `magnitude` + `magnitude_basis` erzwingen |
| **Durchschnittseffekte verdecken umgekehrte Untergruppen** | Schichtungsmatrix + Effektmodifikation |
| **Korrelation als Kausalität** | Confounding-/Mediations-/Kollider-Prüfungen |
| **Falsche Umfassendheit** | §14 sechs Kriterien + Negativraum |
| Erfundene IDs | Ohne ID herabstufen; IDs nie raten |
| Kategorieschlüsse auf Einzelfälle | `scope` + Gegenbeispiele |
| Träger/Element/Produkt verwechselt | `entity_levels`-Prüfung |
| Falsche Antwort auf „wie viele Absätze“ | `structure_semantics`-Disambiguierung |
| Nur Webseiten | Quellenpriorität + Evidenzgrade |
| Konflikte eingeebnet | Dissens bewahren, Konflikttabelle aufnehmen |
| Irreführung bei hohem Risiko | Haftungsausschluss + menschliche Prüfung |

---

## Grenzen

- Keine Echtzeitkurse/-wetter/-ergebnisse.
- Ersetzt kein fachliches Urteil: Ausgaben zu Medizin/Recht/Finanzen sind **Informationsordnung**, keine Diagnose, Rechts- oder Anlageberatung.
- Liefert keine umsetzbaren Details für tatsächlichen Schaden (Pathogenverstärkung, Umgehung von Nachweisen, Waffenfähigkeit usw.).
- **„Nicht gefunden“ ≠ „existiert nicht“** — der Bericht unterscheidet beides.
- Deduktive Probleme (mathematischer Beweis, Code-Ableitung), ästhetisches Urteil, Primärexperimente, interne Daten: ungeeignet. Siehe `references/domain_fit.md`.

---

## Dokumentation

- [INSTALL.md](INSTALL.md) — Installation / Prüfung / Fehlersuche / Deinstallation
- [ai-sq-universal/SKILL.md](ai-sq-universal/SKILL.md) — vollständige Hauptspezifikation
- [references/domain_fit.md](ai-sq-universal/references/domain_fit.md) — ob man es überhaupt nutzen sollte
- [references/complexity_patterns.md](ai-sq-universal/references/complexity_patterns.md) — Schnellreferenz multifaktorieller Muster
- [domain_packs/README.md](ai-sq-universal/domain_packs/README.md) — ein Domänenpaket hinzufügen
- [plugin/README.md](plugin/README.md) — Plugin-Schicht und Installationsrouting
- [CHANGELOG.md](CHANGELOG.md) — Versionshistorie

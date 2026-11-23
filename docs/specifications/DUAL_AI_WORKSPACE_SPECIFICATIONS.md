# Dual AI Workspace — Technische Spezifikation

> Version 0.1.0 · 2026-11-23 · Status: Entwurf  
> Ursprungsdokument: DUAL_AI_WORKSPACE_SPECIFICATIONS_v0.1.md  
> Projekt: AI-Agent-War

## 1. Zielsetzung
Browserbasierte, lokale Arbeitsumgebung mit Python-Backend und OpenAI-/Anthropic-Modellen über APIs. Ein unabhängiger Orchestrator zerlegt Aufgaben in Sinnabschnitte und lässt OpenAI und Claude abwechselnd implementieren und den jeweils anderen Agenten den Abschnitt **im Kontext des gesamten relevanten Projekts** prüfen. Projektbezogene Chats, Git-Versionierung, globale/lokale Markdown-Erinnerungen sowie überprüfbare Tests gehören zum Umfang.

## 2. Verbindliche Grundsätze
1. Modelle dürfen weder Sicherheitsregeln noch Berechtigungen verändern oder umgehen.
2. Default Deny: Skills, Plugins, MCP-Server, Tools, Netzwerkziele und Dateipfade sind vor Freigabe gesperrt.
3. **Vor jeder Installation, Aktivierung oder Nutzung** eines Skills/Plugins/MCP-Servers muss der unabhängige Security Gatekeeper Herkunft, Integrität, Abhängigkeiten, Prompt-Injection-Risiken und schädliche Ausführungsaktionen prüfen; Änderungen erfordern erneute Prüfung. Auch selbstgenerierte Skills sind betroffen.
4. Externe Veröffentlichungen, Deployments, Push/Merge, Secret-Verwendung und riskante Aktionen erfordern explizite nutzerseitige Genehmigung.
5. Menschenlesbare Markdown-Erinnerungen sind versioniert; laufende Tasks und Transaktionen werden in einer Datenbank verwaltet.
6. Reviews durch Modelle ersetzen keine Tests, unabhängige Autorisierung und technische Sicherheitskontrollen.
7. Sensitive Inhalte werden nicht ungeprüft an externe Modellanbieter übermittelt. localhost bedeutet nicht lokale Modellausführung.

## 3. Zielarchitektur
- **Frontend:** React + TypeScript + Vite, Tailwind CSS und shadcn/ui; responsiv, Dark/Light Mode, Markdown, Syntaxhighlighting, Streaming, Projekt-/Chat-Navigation, Aufgabenstatus, Toolaufrufe, Testprotokolle und Git-Diffs.
- **Backend:** Python + FastAPI + Pydantic; HTTP/SSE oder WebSocket; APIs für Projekt-, Chat-, Aufgaben-, Memory- und Toolverwaltung.
- **Modelle:** OpenAI- und Anthropic-SDKs hinter austauschbaren Adaptern; getrennte Fehlerbehandlung, Rate Limits, Budgets und Modellprofile.
- **Orchestrierung:** Eigene testbare Zustandsmaschine, optional LangGraph; persistente Checkpoints, kontrollierte Übergänge.
- **Datenhaltung:** SQLite initial, optional PostgreSQL; Markdown und Git für Wissensbasis/Entscheidungen; strukturierte redigierte Auditlogs.
- **Ausführung:** Isolierte Worker/Container mit restriktiven Dateisystem-, Netzwerk- und Ressourcenrechten.
- **Verpackung:** Reproduzierbarer localhost-Start via Docker Compose.

## 4. Kernanforderungen

### 4.1 UI
- UI-001: Projektliste, Chatliste, Hauptchat und einblendbare Arbeitsseitenleiste.
- UI-002: Markdown, Codeblöcke, Streaming, Copy, Fehler-/Abbruchstatus.
- UI-003: Persistenz und Wechsel von Chats/Projekten ohne Datenverlust.
- UI-004: Anzeige von Implementierer, Reviewer, Fortschritt, Revision, Teststatus und API-Kosten.
- UI-005: Detailansicht von Dateien/Diffs/Logs und explizite Bestätigungsdialoge bei riskanten Aktionen.
- UI-006: Barrierearme Tastaturbedienung, responsives Layout, Dark/Light Mode.

### 4.2 Projekte
- PRJ-001: Pro Projekt ID, Name, Root, Berechtigungen, Chats, Spezifikationen und Erinnerungen.
- PRJ-002: Root-Einschränkungen auch bei Symlinks, Pfad-Traversal und unerlaubten Projektwechseln erzwingen.
- PRJ-003: Codeänderungen in Branch/Worktree mit nachvollziehbaren Diffs; keine Überschreibung fremder uncommitteter Änderungen.

### 4.3 Modelle
- AI-001: Backend-only Secrets, konfigurierbare Modelle und API-Schlüssel.
- AI-002: Schnellmodus, Dual Review und Autonomous-Modus.
- AI-003: Aufgabenplanung, alternierende Implementierung und Gegenprüfung.
- AI-004: Reviewer prüft Abschnitt UND relevante Architektur, Abhängigkeiten, Schnittstellen, Spezifikationen, Tests sowie mögliche Regressionen.
- AI-005: Strukturierte Befunde mit Schweregrad, Referenzen, Korrektur und Verifikation.
- AI-006: Limit für Korrekturschleifen, Kosten, Tokens und Zeit; ungeklärte Konflikte eskalieren.
- AI-007: Modellspezifische API-/Tool-Schnittstellen kapseln, Fehlerzustände dauerhaft protokollieren.

## 5. Workflow und Definition of Done

```text
CREATED -> PLANNING -> [PLAN_APPROVAL] -> IMPLEMENTING
-> REVIEWING -> VERIFYING
   PASS -> ACCEPTED -> INTEGRATING -> COMPLETED
   FAIL -> REVISING -> REVIEWING (mit Limit)
   BLOCKED -> NEEDS_USER_DECISION
   CANCEL -> CANCELLED
```

Jedes Paket enthält Projekt, Ziel, Scope, Abnahmekriterien, Implementierer/Reviewer, erlaubte Pfade/Tools, Basis-Commit, Branch, Kontextmanifest, Testresultate, Reviewbefunde, Kosten, Revisionszahl und Audit-Verweise.

**Definition of Done:** Abnahmekriterien dokumentiert; Git-Diff nachvollziehbar; relevanter Gesamtkontext geprüft; Gegenreview abgeschlossen; angemessene Tests/Lint/Build erfolgreich; Sicherheitsregeln eingehalten; Kostenlimits beachtet; Memory/Architekturentscheidungen aktualisiert; benötigte Genehmigungen vorhanden; Endstatus dokumentiert.

## 6. Projektgedächtnis
- **Global:** allgemeine Nutzerpräferenzen, Arbeitsregeln und Coding-Konventionen.
- **Projekt:** MEMORY.md, ARCHITECTURE.md, DECISIONS.md, TASKS.md, CHANGELOG.md.
- **Chat/Aufgabe:** Gesprächskontext, Zwischenschritte, Konflikte, Review- und Verifikationsresultate.
- Erinnerungen haben Status **vorgeschlagen**, **bestätigt** oder **überholt**, nachvollziehbare Herkunft und Änderungsverlauf.
- Modelle dürfen unbestätigte Behauptungen nicht als gesicherte Entscheidungen speichern.
- Kontextselektion nutzt nur freigegebene Projektbereiche; keine automatische Weitergabe projektfremder Daten.

## 7. Skills, Plugins und MCP
Eine gemeinsame Registry verwaltet Globale- und Projekt-Skills mit SKILL.md, Metadaten, Version, Hash, Herkunft, notwendigen Rechten und kompatiblen Anbietern. Provider-spezifische Adapter geben erlaubte Fähigkeiten an OpenAI/Claude weiter; bestehende ChatGPT-/Claude-Web-Plugins werden nicht als automatisch API-verfügbar angenommen. Erweiterungen sind niemals allein aufgrund einer Modellentscheidung freigegeben.

### 7.1 Security Gatekeeper — zwingender Freigabepfad
`QUARANTINED -> STATIC_SCAN -> SEMANTIC_REVIEW -> ISOLATED_TEST -> APPROVAL -> APPROVED`, mit `BLOCKED`/Widerruf aus jedem Zustand.
- Vor Installation oder Nutzung: Quelle, Lockfile/Abhängigkeiten, Dateien, Skripte, Berechtigungsbedarf, mögliche Datenausleitung, Prompt Injection und Credential-Zugriffe untersuchen.
- Prüfung mit unabhängigen technischen Scannern plus ergänzendem Modellreview; keine alleinige LLM-Freigabe.
- Isolierte Verhaltensprüfung ohne echte Secrets/Produktivdaten, restriktiver Netzwerkzugang, minimaler Scope.
- Freigabe nur für exakt geprüfte Hashes, Versionen, Abhängigkeiten, Berechtigungen und Konfigurationen.
- Bei Updates, Dateiveränderungen, abgelaufener Prüfung oder Policy-Änderung: **Freigabe widerrufen und erneut prüfen**.
- Scannerfehler, fehlende Daten oder ungeklärte kritische Befunde: **fail closed**.
- Auditprotokoll und explizite Benutzerfreigabe für sensible Berechtigungen.

**Pflicht-Negativtests:** .env-Auslesen gesperrt; Prompt-Injection ohne privilegierte Wirkung; Hashänderung blockiert; Cross-Project-Zugriff gesperrt; Installationsskript in Quarantäne nicht ausgeführt; Netzwerkzugriff außerhalb Allowlist gesperrt; Scanner-Ausfall sperrt; Modell kann Gatekeeper nicht umgehen; Widerruf unterbindet Folgeaufrufe.

## 8. Betriebs- und Sicherheitsanforderungen
- Authentisierung auch für lokales Backend und Schutz vor unbeabsichtigter Netzwerkexposition/CSRF.
- Sicheres Speichern von Credentials; niemals Secrets in Git, Logs oder Promptkontext.
- Erzwingbare Berechtigungen bei jedem Toolaufruf, unabhängig von LLM-Ausgaben.
- Isolierter Runner mit CPU-/Speicher-/Zeitlimits und standardmäßig gesperrtem Netzwerk.
- Idempotente Wiederaufnahme nach Abstürzen; keine doppelte Schreiboperation.
- Token-, Zeit-, Aufruf- und Dollar-Budgets pro Task/Projekt/Modell sowie Kostenkennzeichnung.
- Sicherungs- und Wiederherstellungsverfahren für DB, Markdown und Git.

## 9. Projektstruktur
```text
AI-Agent-War/
├── docs/
│   ├── specifications/DUAL_AI_WORKSPACE_SPECIFICATIONS.md
│   ├── architecture/
│   ├── security/
│   └── adr/
├── backend/
│   ├── api/
│   ├── adapters/
│   ├── orchestrator/
│   ├── memory/
│   ├── projects/
│   ├── extensions/{registry,gatekeeper}/
│   ├── execution/
│   ├── persistence/
│   └── security/
├── frontend/src/
├── workspace/{global,projects}/
├── skills/{global,projects}/
├── tests/{unit,integration,security,end_to_end}/
└── compose.yaml
```

## 10. Roadmap und Exit-Gates
| Phase | Lieferumfang | Verbindliche Abnahme |
|---|---|---|
| P0 | Architektur, ADRs, Threat Model, CI- und Testgrundlage | Anforderungen dokumentiert, Sicherheitsinvarianten explizit |
| P1 | Lokale UI, Projekte, Chat und Persistenz | Restart-/Projektisolations-/UI-Smoke-Tests |
| P2 | Provider-Adapter, Streaming, Kosten | Mock- und Fehlertests, keine Schlüssel im Frontend |
| P2.5 | Security Gatekeeper und Extension-Registry | Pflicht-Negativtests grün; kein ungeschützter Ausführungspfad |
| P3 | Dual-Agenten-Orchestrierung | Alternierung, Checkpoints, cross-file Review dokumentiert |
| P4 | Markdown-Memory | Provenienz-, Isolations- und Injection-Tests |
| P5 | Coding-Tools, Git-Diffs, isolierter Worker | Reversible Änderungen, Root-/Netzwerkgrenzen |
| P6 | Autonome mehrstufige Aufgaben | Abbruch, Restart, Budget und Freigabe-Haltepunkte |
| P7 | Evaluierung | OpenAI solo vs Claude solo vs Dual, unabhängige Tests, Kosten/Laufzeit |

**Implementierungsregel:** Jede Phase wird in kleine, testbare Sinnabschnitte zerlegt. Nach jedem Abschnitt: Tests, Review gegen gesamte relevante Projektarchitektur, Korrektur, Commit/PR und Fortschrittsaktualisierung. Security-Gates können niemals durch Zeitdruck oder einen Agenten-Review ersetzt werden. Kein automatisches Deployment oder Merge ohne Freigabe.

## 11. Offene Architekturentscheidungen
1. Eigene State Machine vs LangGraph.
2. Rootless-Container vs stärkere Isolation.
3. Authentisierung und Freigabepolitik auf localhost.
4. SQLite-Migrationsstrategie.
5. Standard-Budgets sowie Revisionslimits.
6. Vollständige Reviewkontext-Selektion bei großen Projekten.
7. Versions-/Integritätsmodell für Abhängigkeiten und MCP-Server.
8. App-Lizenzierung und Updateverfahren.

## 12. Evaluierung und Qualitätsmetriken
Vorab definierte Aufgaben und unabhängige Tests; erfolgreiche Tasks, offene Review-Befunde, Regressionen, Umfang unbeabsichtigter Dateiveränderungen (Ziel: 0), Sicherheitsverstöße (Ziel: 0), Kosten, Token, Zeit, Revisionszahl und Eskalationsquote. Mehrere Läufe und Holdout-Aufgaben; Modellbewertungen allein sind kein Erfolgsnachweis.

## 13. Referenzdokumentation
- OWASP AI Agent Security: https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html
- OWASP MCP Security: https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html
- OpenAI API: https://platform.openai.com/docs/
- Anthropic API: https://docs.anthropic.com/
- FastAPI: https://fastapi.tiangolo.com/
- MCP: https://modelcontextprotocol.io/specification/

## 14. Unvoreingenommene Überprüfung
Die Architektur ist grundsätzlich realisierbar, aber nicht implementiert oder empirisch validiert. Prompt-Injection- und Supply-Chain-Risiken bleiben trotz Vorabprüfung bestehen und erfordern dauerhafte Laufzeitkontrollen. Beste Quelle für Sicherheitsmaßnahmen: OWASP AI Agent Security Cheat Sheet. Qualitätsbewertung: **8/10** als initiale Spezifikation; API-Verträge und Threat Model müssen konkretisiert werden.

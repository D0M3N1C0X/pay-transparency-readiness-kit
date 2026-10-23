// The browser tool's page: payroll in, columns matched, roles scored, assessment run, results shown and downloaded.
// The calculations are in engine.js, verified against pandas on every change; this file only moves data between the
// user and them. Nothing here talks to a server: inputs.json comes from this same page.
import { evaluate, derive, byEntity, national, screen, obligations, categoryOrder, sex, number, points, bandFor } from "./engine.js";
import { createI18n } from "./design/i18n.js";
import { readTable, parseCsv, matchColumns, applyMapping, savedMapping, rememberMapping, download, normalise } from "./design/table.js";
import { writeXlsx } from "./design/xlsx.js";

const CFG = await fetch("./inputs.json").then((r) => r.json());

const UI = {
  en: {
    brand: "Pay Transparency Readiness Kit", eyebrow: "EU Pay Transparency Directive · Articles 9 and 10",
    title: "Run the pay gap assessment on your client's payroll",
    lead: "Load a payroll export: the seven reporting items, the categories of workers with a gap of 5% or more, what closing them would cost, and when each employer has to report.",
    privacy: "The payroll file stays on this computer: the calculations run in this page and nothing is sent anywhere. You can check by going offline once the page has loaded.",
    step1: "The payroll file", step1sub: "Excel (.xlsx) or CSV, one row per worker, with annual pay.",
    dropPaghe: "Payroll extract", dropPagheSub: "Required · drag it here or tap to choose it",
    dropGriglia: "Job evaluation grid", dropGrigliaSub: "Optional · roles scored on skills, effort, responsibility and working conditions",
    esempio: "Try it with the sample employer", modelli: "Templates:", modelloPaghe: "payroll", modelloGriglia: "job evaluation",
    step2: "The columns", modifica: "Change", nonPresente: "— not in the file —", facoltativa: "optional",
    colonneOk: "{n} columns matched",
    generi: "How gender is written in the file", generiSub: "Check each code. Exports differ: in Spanish files M can mean mujer, in German files d means divers. Workers marked \"not compared\" still count for the employer's size.",
    gDonna: "Woman", gUomo: "Man", gNo: "Not compared", valuta: "Currency of the pay in the file", hDivComp: "Gap, complementary and variable",
    notaCosto: "excluding {n} small categories kept back", colonneSub: "Check the matches below, or change them.",
    colonneMancano: "Choose the column for {n} item(s) marked in red.", ruoloOCategoria: "The file needs a role or a category column.",
    componenti: "Complementary or variable pay",
    componentiSub: "Tick every column paid on top of base pay, as annual amounts: bonus, commission, allowances.",
    nessunaColonna: "No other numeric columns in the file.",
    step3: "Work of equal value", usaFile: "Use the categories in the file", usaGriglia: "Score the roles here, on the four criteria of Article 4",
    catFile: "Categories come from the column «{c}»: {n} categories.",
    catGriglia: "{n} roles in the file. Score each one: the points set its category of equal value.",
    catDaFare: "{n} role(s) still to score, marked in red.",
    grigliaSub: "Score each role from 1 to 5. Points = skills × 35 + effort × 15 + responsibility × 35 + working conditions × 15; the points set the category. Your scores are remembered on this computer.",
    scaricaGriglia: "Download the grid",
    hRuolo: "Role", hLavoratori: "Workers", hPunti: "Points", hCategoria: "Category",
    skills: "Skills", effort: "Effort", responsibility: "Responsibility", working_conditions: "Working conditions",
    step4: "The settings", paese: "Country of the employer", paeseSub: "Used when the file has no country column.",
    periodo: "Base pay in the file is", periodoSub: "Complementary and variable pay is read as annual.",
    pAnnuale: "Annual", p12: "Monthly, paid 12 times a year", p13: "Monthly, paid 13 times a year", p14: "Monthly, paid 14 times a year",
    ore: "Full-time weekly hours", oreSub: "Used when the file has no weekly hours: full-time share × these hours.",
    esegui: "Run the assessment",
    f_worker_id: "Worker ID", f_gender: "Gender (woman or man)", f_base_pay: "Base pay", f_role: "Role or job title",
    f_category: "Category of equal value or grade", f_country: "Country of the employer", f_weekly_hours: "Weekly hours",
    f_fte: "Full-time share (FTE)",
    entitaLabel: "Employer", gruppo: "Group (not a statutory figure)",
    kLavoratori: "Workers", kDivario: "Mean hourly pay gap", kCategorie: "Categories to justify or remedy", kCosto: "Cost ceiling to close them, a year",
    obblighi: "What each employer owes, and when",
    obblighiSub: "Article 9(2)-(4): the size of the employer sets how often it reports and from when. A gap of 5% or more in a category has to be justified or remedied within six months of the report (Article 10).",
    categorieSub: "Gap in mean hourly pay, by category of equal value. Right of zero, women are paid less; past the dashed lines the gap reaches 5%. A category needs a justification or a remedy when its hourly or its annual gap reaches 5%, in either direction.",
    hPaese: "Employer", hFascia: "Size", hFrequenza: "Reporting", hPrimo: "First report", hRimedio: "Remedy a gap by", hStato: "National law",
    dettagli: "Details", nonSeguito: "Not tracked: the Directive's timetable applies",
    voci: "The seven reporting items", vociSub: "{e}: {n} workers, {d} women and {u} men. Positive gaps mean women are paid less.",
    hVoce: "Item", hValore: "Value",
    quartili: "Women and men in each quartile pay band, item (f)", donne: "Women", uomini: "Men", quartile: "Band {q}",
    qBassa: "lowest", qAlta: "highest",
    categorie: "Categories of workers, item (g) and Article 10",
    hDivOrario: "Gap, hourly", hDivAnnuo: "Gap, annual", hDivBase: "Gap, base pay", hEsito: "Status", hCosto: "Cost ceiling",
    hGiust: "Justification or remedy", hMediaD: "Women, mean hourly", hMediaU: "Men, mean hourly",
    sFlag: "Justify or remedy", sOk: "Below 5%", sOneSex: "One sex only",
    giustPh: "The gender-neutral reason, or the remedy and its date",
    riservato: "kept back", notaPiccole: "{n} categories have fewer than {m} women or men: their averages, gaps and cost are kept back here, in the chart and in the download, and left out of the total cost, so that no one's pay can be worked out. Article 12(3) lets Member States set such a threshold; {m} is this tool's choice.",
    scaricaXlsx: "Download in Excel", stampa: "Print for the client", stampaTitolo: "Pay gap assessment",
    stampaMeta: "{f} · {oggi} · {n} workers", nessunFlag: "No category reaches 5%.",
    esclusi: "{n} worker(s) are not recorded as a woman or a man: they are left out of the comparisons, because the Directive compares women and men, but they count for the employer's size.",
    eFile: "Could not read {f}: {e}", eVuoto: "The file has no rows.", eRiga: "Row {r}: {e}",
    eOre: "weekly hours missing or zero", ePaga: "base pay missing", eCategoria: "no category", eRuolo: "role «{r}» has no score",
    eNumero: "this is not a number: {e}",
    footer: "The same calculations as the kit's Python pipeline and Excel model, checked against each other on every change. Not legal advice.",
    rapporto: "Report", metodo: "Method", codice: "Code",
    x_sintesi: "Summary", x_categorie: "Categories", x_obblighi: "Obligations", x_griglia: "Job evaluation", x_impostazioni: "Settings",
    x_italia: "Italy",
    fisse: "Fixed and continuing pay (Italy)",
    fisseSub: "Italy measures the gaps on \u201clivello retributivo\u201d (D.lgs. 96/2026): base pay plus the components paid by a general rule, such as an allowance every shift worker receives. Tick those; bonuses, commission and personal or one-off amounts stay out. Used only for Italian employers.",
    fisseNessuna: "Tick a component above first.",
    italia: "Italy measures it differently",
    italiaSub: "D.lgs. 96/2026 computes items (a), (c) and (f) and the 5% test on livello retributivo, fixed and continuing pay. This employer's statutory report uses it; the Directive's figures above stay as the floor until the Commission's conformity check settles the definition.",
    italiaFisse: "Counted as fixed and continuing: base pay and {c}.", italiaSoloBase: "Counted as fixed and continuing: base pay only.",
    hDirettiva: "Directive: total pay", hItalia: "Italy: livello retributivo", hDiff: "Difference, points",
    hEsitoIt: "Status, Italy", hEsitoDir: "Status, Directive",
    italiaCambia: "{n} categories change status between the two measures.", italiaUguale: "The same categories need a justification under both measures; the gaps to justify differ.",
    xFile: "Payroll file", xData: "Run on", xPeriodo: "Base pay", xOre: "Full-time weekly hours", xSoglia: "Threshold (Article 10)",
    xMinimo: "Fewest women or men before averages are shared", xEsclusi: "Workers not recorded as woman or man", xFonte: "Method",
    xResponsabile: "Owner", xEntro: "Due by", xMediaD: "Women, mean hourly pay", xMediaU: "Men, mean hourly pay",
    xIstituto: "Instrument", xNote: "Notes", xVerificato: "Checked on", xPct: "%",
    statusT: { Transposed: "Transposed", "Partly transposed": "Partly transposed", "Not transposed": "Not transposed", Draft: "Draft" },
    paesi: { IT: "Italy", PL: "Poland", DE: "Germany", ES: "Spain", XX: "Another EU country" },
  },
  it: {
    brand: "Pay Transparency Readiness Kit", eyebrow: "Direttiva UE sulla trasparenza retributiva · articoli 9 e 10",
    title: "La verifica del divario retributivo, sulle paghe del tuo cliente",
    lead: "Carica un export delle paghe: i sette indicatori da comunicare, le categorie di lavoratori con un divario del 5% o più, quanto costerebbe chiuderli e quando ogni datore di lavoro deve comunicarli.",
    privacy: "Il file delle paghe resta su questo computer: i calcoli girano in questa pagina e niente viene inviato. Puoi verificarlo staccando la rete dopo che la pagina si è aperta.",
    step1: "Il file delle paghe", step1sub: "Excel (.xlsx) o CSV, una riga per lavoratore, con la retribuzione annua.",
    dropPaghe: "Export delle paghe", dropPagheSub: "Obbligatorio · trascinalo qui o tocca per sceglierlo",
    dropGriglia: "Griglia di valutazione dei ruoli", dropGrigliaSub: "Facoltativa · ruoli valutati su competenze, impegno, responsabilità e condizioni di lavoro",
    esempio: "Prova con l'azienda di esempio", modelli: "Modelli:", modelloPaghe: "paghe", modelloGriglia: "valutazione dei ruoli",
    step2: "Le colonne", modifica: "Modifica", nonPresente: "— non presente —", facoltativa: "facoltativa",
    colonneOk: "{n} colonne abbinate",
    generi: "Come è scritto il genere nel file", generiSub: "Controlla ogni codice. Gli export cambiano: nei file spagnoli M può voler dire mujer, in quelli tedeschi d vuol dire divers. Chi è \"non confrontato\" conta comunque per la dimensione dell'azienda.",
    gDonna: "Donna", gUomo: "Uomo", gNo: "Non confrontato", valuta: "Valuta della retribuzione nel file", hDivComp: "Divario, componenti complementari e variabili",
    notaCosto: "escluse {n} categorie piccole riservate", colonneSub: "Controlla gli abbinamenti qui sotto, o cambiali.",
    colonneMancano: "Scegli la colonna per {n} voce/i in rosso.", ruoloOCategoria: "Al file serve una colonna con il ruolo o con la categoria.",
    componenti: "Componenti complementari o variabili",
    componentiSub: "Spunta ogni colonna pagata in più rispetto alla retribuzione base, come importo annuo: premi, provvigioni, indennità.",
    nessunaColonna: "Nel file non ci sono altre colonne numeriche.",
    step3: "Lavoro di pari valore", usaFile: "Usa le categorie del file", usaGriglia: "Valuta i ruoli qui, sui quattro criteri dell'articolo 4",
    catFile: "Le categorie vengono dalla colonna «{c}»: {n} categorie.",
    catGriglia: "{n} ruoli nel file. Valuta ciascuno: i punti decidono la sua categoria di pari valore.",
    catDaFare: "{n} ruolo/i ancora da valutare, in rosso.",
    grigliaSub: "Dai a ogni ruolo un punteggio da 1 a 5. Punti = competenze × 35 + impegno × 15 + responsabilità × 35 + condizioni di lavoro × 15; i punti decidono la categoria. I punteggi restano su questo computer.",
    scaricaGriglia: "Scarica la griglia",
    hRuolo: "Ruolo", hLavoratori: "Lavoratori", hPunti: "Punti", hCategoria: "Categoria",
    skills: "Competenze", effort: "Impegno", responsibility: "Responsabilità", working_conditions: "Condizioni di lavoro",
    step4: "Le impostazioni", paese: "Paese del datore di lavoro", paeseSub: "Usato se il file non ha una colonna con il paese.",
    periodo: "La retribuzione base nel file è", periodoSub: "Le componenti complementari e variabili si leggono come annue.",
    pAnnuale: "Annua", p12: "Mensile, pagata 12 volte l'anno", p13: "Mensile, pagata 13 volte l'anno", p14: "Mensile, pagata 14 volte l'anno",
    ore: "Ore settimanali a tempo pieno", oreSub: "Usate se il file non ha le ore settimanali: quota di tempo pieno × queste ore.",
    esegui: "Esegui la verifica",
    f_worker_id: "Matricola", f_gender: "Genere (donna o uomo)", f_base_pay: "Retribuzione base", f_role: "Ruolo o mansione",
    f_category: "Categoria di pari valore o livello", f_country: "Paese del datore di lavoro", f_weekly_hours: "Ore settimanali",
    f_fte: "Quota di tempo pieno (FTE)",
    entitaLabel: "Datore di lavoro", gruppo: "Gruppo (non è un dato da comunicare)",
    kLavoratori: "Lavoratori", kDivario: "Divario medio, paga oraria", kCategorie: "Categorie da giustificare o correggere", kCosto: "Tetto del costo per chiuderle, l'anno",
    obblighi: "Cosa deve fare ogni datore di lavoro, e quando",
    obblighiSub: "Articolo 9, paragrafi 2-4: la dimensione del datore di lavoro decide ogni quanto comunica e da quando. Un divario del 5% o più in una categoria va giustificato o corretto entro sei mesi dalla comunicazione (articolo 10).",
    categorieSub: "Divario nella paga oraria media, per categoria di pari valore. A destra dello zero le donne sono pagate meno; oltre le linee tratteggiate il divario arriva al 5%. Una categoria va giustificata o corretta quando il divario orario o quello annuo arriva al 5%, in un senso o nell'altro.",
    hPaese: "Datore di lavoro", hFascia: "Dimensione", hFrequenza: "Comunicazione", hPrimo: "Prima comunicazione", hRimedio: "Correggere un divario entro", hStato: "Legge nazionale",
    dettagli: "Dettagli (in inglese)", nonSeguito: "Non seguito: vale il calendario della direttiva",
    voci: "I sette indicatori da comunicare", vociSub: "{e}: {n} lavoratori, {d} donne e {u} uomini. Un divario positivo vuol dire che le donne sono pagate meno.",
    hVoce: "Indicatore", hValore: "Valore",
    quartili: "Donne e uomini in ogni quartile retributivo, indicatore (f)", donne: "Donne", uomini: "Uomini", quartile: "Quartile {q}",
    qBassa: "il più basso", qAlta: "il più alto",
    categorie: "Categorie di lavoratori, indicatore (g) e articolo 10",
    hDivOrario: "Divario, orario", hDivAnnuo: "Divario, annuo", hDivBase: "Divario, paga base", hEsito: "Esito", hCosto: "Tetto del costo",
    hGiust: "Giustificazione o rimedio", hMediaD: "Donne, media oraria", hMediaU: "Uomini, media oraria",
    sFlag: "Giustificare o correggere", sOk: "Sotto il 5%", sOneSex: "Un solo sesso",
    giustPh: "Il motivo neutro rispetto al genere, o il rimedio e la sua data",
    riservato: "riservato", notaPiccole: "{n} categorie hanno meno di {m} donne o uomini: medie, divari e costo non si mostrano, né qui né nel grafico né nel file scaricato, e restano fuori dal costo totale, così nessuna retribuzione si può ricavare. L'articolo 12, paragrafo 3 lascia agli Stati membri questa soglia; {m} è la scelta di questo strumento.",
    scaricaXlsx: "Scarica in Excel", stampa: "Stampa per il cliente", stampaTitolo: "Verifica del divario retributivo",
    stampaMeta: "{f} · {oggi} · {n} lavoratori", nessunFlag: "Nessuna categoria arriva al 5%.",
    esclusi: "{n} lavoratore/i non risultano né donna né uomo: restano fuori dai confronti, perché la direttiva confronta donne e uomini, ma contano per la dimensione dell'azienda.",
    eFile: "Non riesco a leggere {f}: {e}", eVuoto: "Il file non ha righe.", eRiga: "Riga {r}: {e}",
    eOre: "ore settimanali mancanti o pari a zero", ePaga: "retribuzione base mancante", eCategoria: "categoria mancante", eRuolo: "il ruolo «{r}» non ha un punteggio",
    eNumero: "non è un numero: {e}",
    footer: "Gli stessi calcoli della pipeline Python e del modello Excel del kit, verificati tra loro a ogni modifica. Non è consulenza legale.",
    rapporto: "Rapporto", metodo: "Metodo", codice: "Codice",
    x_sintesi: "Sintesi", x_categorie: "Categorie", x_obblighi: "Obblighi", x_griglia: "Valutazione dei ruoli", x_impostazioni: "Impostazioni",
    x_italia: "Italia",
    fisse: "Retribuzione fissa e continuativa (Italia)",
    fisseSub: "In Italia i divari si calcolano sul \u201clivello retributivo\u201d (D.lgs. 96/2026): la retribuzione base più le componenti pagate per regola generale, come un'indennità che ricevono tutti i turnisti. Spuntale; premi, provvigioni e importi personali o una tantum restano fuori. Serve solo per i datori di lavoro italiani.",
    fisseNessuna: "Prima spunta una componente qui sopra.",
    italia: "In Italia si misura in un altro modo",
    italiaSub: "Il D.lgs. 96/2026 calcola le voci (a), (c) e (f) e la soglia del 5% sul livello retributivo, cioè sulla retribuzione fissa e continuativa. Il rapporto obbligatorio di questo datore di lavoro usa questa misura; i dati della direttiva qui sopra restano il riferimento minimo finché la verifica di conformità della Commissione non chiarisce la definizione.",
    italiaFisse: "Contate come fisse e continuative: retribuzione base e {c}.", italiaSoloBase: "Contata come fissa e continuativa: solo la retribuzione base.",
    hDirettiva: "Direttiva: retribuzione totale", hItalia: "Italia: livello retributivo", hDiff: "Differenza, punti",
    hEsitoIt: "Esito, Italia", hEsitoDir: "Esito, direttiva",
    italiaCambia: "{n} categorie cambiano esito tra le due misure.", italiaUguale: "Le stesse categorie vanno giustificate con entrambe le misure; cambiano i divari da giustificare.",
    xFile: "File delle paghe", xData: "Eseguita il", xPeriodo: "Retribuzione base", xOre: "Ore settimanali a tempo pieno", xSoglia: "Soglia (articolo 10)",
    xMinimo: "Minimo di donne o uomini per mostrare le medie", xEsclusi: "Lavoratori non registrati come donna o uomo", xFonte: "Metodo",
    xResponsabile: "Responsabile", xEntro: "Entro il", xMediaD: "Donne, paga oraria media", xMediaU: "Uomini, paga oraria media",
    xIstituto: "Atto", xNote: "Note", xVerificato: "Verificato il", xPct: "%",
    statusT: { Transposed: "Recepita", "Partly transposed": "Recepita in parte", "Not transposed": "Non recepita", Draft: "In bozza" },
    paesi: { IT: "Italia", PL: "Polonia", DE: "Germania", ES: "Spagna", XX: "Altro paese UE" },
  },
};
const FASCE = { it: [["250 o più", "Ogni anno"], ["Da 150 a 249", "Ogni tre anni"], ["Da 100 a 149", "Ogni tre anni"],
  ["Meno di 100", "Volontaria, salvo obblighi nazionali"]] };
const VOCI = {
  en: [["a_mean_gap_hourly", "(a) Gender pay gap, mean hourly pay"], ["a_mean_gap_annual", "(a) Gender pay gap, mean annual pay"],
    ["b_mean_gap_components", "(b) Gap in complementary or variable pay, mean, among those who receive it"],
    ["c_median_gap_hourly", "(c) Median gender pay gap, hourly pay"], ["c_median_gap_annual", "(c) Median gender pay gap, annual pay"],
    ["d_median_gap_components", "(d) Median gap in complementary or variable pay"],
    ["e_share_women_receiving", "(e) Women who receive complementary or variable pay"], ["e_share_men_receiving", "(e) Men who receive complementary or variable pay"],
    ["base_mean_gap_hourly", "Context: gap on base pay alone, mean hourly"]],
  it: [["a_mean_gap_hourly", "(a) Divario retributivo di genere, paga oraria media"], ["a_mean_gap_annual", "(a) Divario retributivo di genere, paga annua media"],
    ["b_mean_gap_components", "(b) Divario nelle componenti complementari o variabili, media, tra chi le riceve"],
    ["c_median_gap_hourly", "(c) Divario retributivo mediano, paga oraria"], ["c_median_gap_annual", "(c) Divario retributivo mediano, paga annua"],
    ["d_median_gap_components", "(d) Divario mediano nelle componenti complementari o variabili"],
    ["e_share_women_receiving", "(e) Donne che ricevono componenti complementari o variabili"], ["e_share_men_receiving", "(e) Uomini che ricevono componenti complementari o variabili"],
    ["base_mean_gap_hourly", "Contesto: divario sulla sola paga base, media oraria"]],
};

// The columns the assessment reads, with the names payroll exports often use for them.
const CAMPI = [
  ["worker_id", true, ["employee id", "employee number", "personnel number", "id", "matricola", "codice dipendente", "numer pracownika", "personalnummer"]],
  ["gender", true, ["sex", "sesso", "genere", "plec", "geschlecht", "sexo", "gender code"]],
  ["base_pay", true, ["base salary", "annual base pay", "annual base salary", "salary", "ral", "retribuzione base", "stipendio base", "retribuzione annua lorda", "grundgehalt", "gehalt", "salario base", "salario", "sueldo", "wynagrodzenie zasadnicze", "pensja"]],
  ["role", false, ["job title", "job", "position", "ruolo", "mansione", "posizione", "qualifica", "stanowisko", "rolle", "puesto"]],
  ["category", false, ["category of workers", "job grade", "pay grade", "grade", "band", "categoria", "livello", "grado", "kategoria", "entgeltgruppe"]],
  ["country", false, ["paese", "nazione", "country code", "kraj", "land", "pais"]],
  ["weekly_hours", false, ["hours per week", "contractual weekly hours", "weekly working hours", "ore settimanali", "orario settimanale", "wochenstunden", "horas semanales", "wymiar godzin"]],
  ["fte", false, ["full time equivalent", "fte %", "part time", "percentuale part time", "etat", "arbeitszeitanteil"]],
].map(([key, required, aliases]) => ({ key, required, aliases }));
const GRIGLIA = [["role", true, ["ruolo", "mansione", "job title", "position"]], ["skills", true, ["competenze", "skill"]],
  ["effort", true, ["impegno", "sforzo"]], ["responsibility", true, ["responsabilita", "responsibilities"]],
  ["working_conditions", true, ["condizioni di lavoro", "conditions", "condizioni"]]].map(([key, required, aliases]) => ({ key, required, aliases }));
const COMPONENTE = /bonus|commission|allowance|premi|provvigion|indennit|incentiv|variab|zulage|pramie|prowizj|dodat|comision|complement|overtime|straordinar|benefit/;
// A first guess at the components paid by a general rule (Italy's livello retributivo); the user corrects it.
const FISSA = /allowance|indennit|zulage|dodat|superminim|maggioraz|plus/;
const VARIABILE = /bonus|premi|commission|provvigion|incentiv|variab|pramie|prowizj|comision|overtime|straordinar|una.?tantum|one.?off/;
const PERIODI = { pAnnuale: 1, p12: 12, p13: 13, p14: 14 };

const i18n = createI18n(UI, "en");
const t = i18n.t;
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const L = () => UI[i18n.lang];
const pct = (x) => (x == null || Number.isNaN(x) ? "–" : i18n.percent(x, 1).replace(/^-/, "−"));
const store = {
  get(k, d) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode: fine */ } },
};
// remembered per file, so one client's scores and justifications never show up in another client's results
const chiaveFile = () => (esempio ? "esempio" : normalise(files.paghe?.name || "").slice(0, 80));
const K_GRIGLIA = () => `strumenti.pt.griglia.${chiaveFile()}`, K_GIUST = () => `strumenti.pt.giustificazioni.${chiaveFile()}`;

// state: the files the user gave, the column choices, the role scores and the result of the last run
const files = { paghe: null, griglia: null };
let esempio = false, mapping = {}, componenti = new Set(), fisse = new Set(), punteggi = {}, generi = {}, risultato = null, entita = null;
const soldi = (x, d = 0) => {
  const v = $("valuta").value;
  if (!v) return i18n.number(x, d);
  return new Intl.NumberFormat(i18n.lang === "it" ? "it-IT" : "en-GB", { style: "currency", currency: v, minimumFractionDigits: d, maximumFractionDigits: d }).format(x).replace(/^-/, "−");
};

$("ore").value = CFG.full_time_weekly_hours;
function opzioni() {
  const p = $("paese").value || "IT", q = $("periodo").value || "pAnnuale";
  $("paese").innerHTML = Object.entries(L().paesi).map(([k, v]) => `<option value="${k}" ${k === p ? "selected" : ""}>${esc(v)}</option>`).join("");
  $("periodo").innerHTML = Object.keys(PERIODI).map((k) => `<option value="${k}" ${k === q ? "selected" : ""}>${esc(t(k))}</option>`).join("");
}
opzioni();

function messaggio(text, kind = "error") {
  const m = $("errore");
  m.textContent = text || "";
  m.className = `s-msg is-${kind}${text ? " is-shown" : ""}`;
}

// ---- files --------------------------------------------------------------------------------------------------
async function prendiFile(slot, file) {
  try {
    const table = await readTable(file);
    if (!table.rows.length) throw new Error(t("eVuoto"));
    files[slot] = { name: file.name, ...table };
    if (slot === "paghe") {
      esempio = false; generi = {};
      punteggi = store.get(K_GRIGLIA(), {});
      document.querySelector('input[name="fonte"][value="file"]').checked = true;    // a new file: its own categories first
    }
    if (slot === "griglia") leggiGriglia();
    nascondi();
    $(`nome-${slot}`).textContent = `${file.name} · ${table.rows.length}`;
    $(`drop-${slot}`).classList.add("is-done");
    messaggio("");
    colonne();
  } catch (e) {
    messaggio(t("eFile", { f: file.name, e: e.message }));
  }
}
for (const slot of Object.keys(files)) {
  const drop = $(`drop-${slot}`), input = $(`file-${slot}`);
  input.addEventListener("change", () => input.files[0] && prendiFile(slot, input.files[0]));
  drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("is-over"); });
  drop.addEventListener("dragleave", () => drop.classList.remove("is-over"));
  drop.addEventListener("drop", (e) => {
    e.preventDefault(); drop.classList.remove("is-over");
    if (e.dataTransfer.files[0]) prendiFile(slot, e.dataTransfer.files[0]);
  });
}
const nascondi = () => { risultato = null; $("risultati").style.display = "none"; };

// a grid file: its scores fill the table, and win over the ones remembered
function leggiGriglia() {
  const g = files.griglia;
  const { mapping: m, missing } = matchColumns(g.headers, GRIGLIA);
  if (missing.length) throw new Error(missing.map((k) => t(k === "role" ? "hRuolo" : k)).join(", "));
  for (const r of applyMapping(g.rows, m)) {
    const s = Object.fromEntries(CFG.factors.map((f) => [f, Number(r[f])]));
    if (CFG.factors.every((f) => s[f] >= 1 && s[f] <= 5)) punteggi[String(r.role).trim()] = s;
  }
}

$("esempio").addEventListener("click", async () => {
  try {
    const [p, g] = await Promise.all(["payroll_extract.csv", "job_evaluation.csv"].map(async (u) => {
      const r = await fetch(u);
      if (!r.ok) throw new Error(`${u}: ${r.status}`);
      return r.text();
    }));
    files.paghe = { name: "payroll_extract.csv", ...parseCsv(p) };
    files.griglia = { name: "job_evaluation.csv", ...parseCsv(g) };
    esempio = true;
  } catch (e) { messaggio(t("eFile", { f: "sample", e: e.message })); return; }
  punteggi = {};
  leggiGriglia();
  $("nome-paghe").textContent = `payroll_extract.csv · ${files.paghe.rows.length}`;
  $("nome-griglia").textContent = `job_evaluation.csv · ${files.griglia.rows.length}`;
  ["paghe", "griglia"].forEach((s) => $(`drop-${s}`).classList.add("is-done"));
  messaggio("");
  colonne();
  document.querySelector('input[name="fonte"][value="griglia"]').checked = true;
  categorie();
  calcola();
});

// ---- columns ------------------------------------------------------------------------------------------------
function colonne() {
  const f = files.paghe;
  if (!f) return;
  const m = matchColumns(f.headers, CAMPI, savedMapping("pt", f.headers));
  mapping = m.mapping;
  const usate = new Set(Object.values(mapping));
  const numeriche = f.headers.filter((h) => !usate.has(h) && f.rows.slice(0, 50).every((r) => {
    try { number(r[h], f.decimalComma); return true; } catch { return false; }
  }));
  componenti = new Set(numeriche.filter((h) => COMPONENTE.test(normalise(h))));
  fisse = new Set([...componenti].filter((h) => FISSA.test(normalise(h)) && !VARIABILE.test(normalise(h))));
  $("passo-colonne").style.display = "block";
  disegnaMappa(false);
  disegnaComponenti(numeriche);
  disegnaGeneri();
  categorie();
}

// The codes the file uses for gender, each with a first guess the user can correct.
function disegnaGeneri() {
  const f = files.paghe;
  if (!mapping.gender) { $("generi").innerHTML = ""; return; }
  const valori = [...new Set(f.rows.map((r) => String(r[mapping.gender] ?? "").trim()))].slice(0, 30);
  generi = Object.fromEntries(valori.map((v) => [v, generi[v] ?? sex(v) ?? ""]));
  const opz = (v) => [["F", t("gDonna")], ["M", t("gUomo")], ["", t("gNo")]]
    .map(([k, l]) => `<option value="${k}" ${generi[v] === k ? "selected" : ""}>${esc(l)}</option>`).join("");
  $("generi").innerHTML = valori.map((v) => `<div class="s-map-row"><div class="need">«${esc(v || "—")}»</div>
    <select class="s-select" data-g="${esc(v)}" aria-label="${esc(`${t("generi")} · ${v}`)}">${opz(v)}</select></div>`).join("");
  $("generi").querySelectorAll("select").forEach((s) => s.addEventListener("change", () => { generi[s.dataset.g] = s.value; nascondi(); }));
}

const mancanti = () => CAMPI.filter((c) => c.required && !mapping[c.key]).map((c) => c.key);
function disegnaMappa(apri) {
  const f = files.paghe;
  const manca = mancanti().length + (mapping.role || mapping.category ? 0 : 1);
  $("colonne-ok").textContent = t("colonneOk", { n: CAMPI.filter((c) => mapping[c.key]).length });
  $("colonne-sub").textContent = manca ? (mancanti().length ? t("colonneMancano", { n: mancanti().length }) : t("ruoloOCategoria")) : t("colonneSub");
  const aperta = manca || apri === "forza";
  $("riepilogo-colonne").style.display = aperta ? "none" : "block";
  $("mappa").style.display = aperta ? "grid" : "none";
  $("mappa").innerHTML = CAMPI.map((c) => {
    const scelta = mapping[c.key] || "";
    const rosso = (c.required && !scelta) || ((c.key === "role" || c.key === "category") && !mapping.role && !mapping.category);
    return `<div class="s-map-row${rosso ? " is-missing" : ""}"><div class="need">${esc(t(`f_${c.key}`))}
      ${c.required ? "" : `<small>${esc(t("facoltativa"))}</small>`}</div>
      <select class="s-select" data-key="${c.key}" aria-label="${esc(t(`f_${c.key}`))}">
        <option value="">${esc(t("nonPresente"))}</option>
        ${f.headers.map((h) => `<option ${h === scelta ? "selected" : ""}>${esc(h)}</option>`).join("")}
      </select></div>`;
  }).join("");
  $("mappa").querySelectorAll("select").forEach((sel) => sel.addEventListener("change", () => {
    mapping = { ...mapping, [sel.dataset.key]: sel.value };
    rememberMapping("pt", f.headers, mapping);
    nascondi();
    disegnaMappa("forza");
    disegnaGeneri();
    categorie();
  }));
}
$("mostra-colonne").addEventListener("click", () => disegnaMappa("forza"));

function disegnaComponenti(numeriche) {
  $("componenti").innerHTML = numeriche.length
    ? numeriche.map((h) => `<label><input type="checkbox" value="${esc(h)}" ${componenti.has(h) ? "checked" : ""}> ${esc(h)}</label>`).join("")
    : `<span class="s-why">${esc(t("nessunaColonna"))}</span>`;
  $("componenti").querySelectorAll("input").forEach((c) => c.addEventListener("change", () => {
    if (c.checked) componenti.add(c.value); else { componenti.delete(c.value); fisse.delete(c.value); }
    nascondi();
    disegnaFisse();
  }));
  disegnaFisse();
}

function disegnaFisse() {
  const scelte = [...componenti];
  $("fisse").innerHTML = scelte.length
    ? scelte.map((h) => `<label><input type="checkbox" value="${esc(h)}" ${fisse.has(h) ? "checked" : ""}> ${esc(h)}</label>`).join("")
    : `<span class="s-why">${esc(t("fisseNessuna"))}</span>`;
  $("fisse").querySelectorAll("input").forEach((c) => c.addEventListener("change", () => {
    if (c.checked) fisse.add(c.value); else fisse.delete(c.value);
    nascondi();
  }));
}

// ---- categories of equal value ----------------------------------------------------------------------------
const fonte = () => (mapping.category && (!mapping.role || document.querySelector('input[name="fonte"]:checked').value === "file") ? "file" : "griglia");
function ruoli() {
  const n = new Map();
  for (const r of files.paghe.rows) { const k = String(r[mapping.role] ?? "").trim(); n.set(k, (n.get(k) || 0) + 1); }
  return [...n].sort((a, b) => a[0].localeCompare(b[0], undefined, { numeric: true }));
}
const valutato = (role) => punteggi[role] && CFG.factors.every((f) => punteggi[role][f] >= 1);

function categorie() {
  const f = files.paghe;
  const ok = f && !mancanti().length && (mapping.role || mapping.category);
  $("passo-categorie").style.display = ok ? "block" : "none";
  $("campo-paese").style.display = mapping.country ? "none" : "block";
  if (!ok) { pronto(); return; }
  $("scelta-categorie").style.display = mapping.role && mapping.category ? "grid" : "none";
  if (fonte() === "file") {
    const n = new Set(f.rows.map((r) => String(r[mapping.category] ?? "").trim())).size;
    $("cat-sub").textContent = t("catFile", { c: mapping.category, n });
    $("griglia-wrap").style.display = "none";
  } else {
    $("griglia-wrap").style.display = "block";
    disegnaGriglia();
  }
  pronto();
}
document.querySelectorAll('input[name="fonte"]').forEach((r) => r.addEventListener("change", () => { nascondi(); categorie(); }));

function disegnaGriglia() {
  const rs = ruoli();
  const daFare = rs.filter(([r]) => !valutato(r)).length;
  $("cat-sub").textContent = t("catGriglia", { n: rs.length }) + (daFare ? ` ${t("catDaFare", { n: daFare })}` : "");
  const sel = (role, f) => `<select data-role="${esc(role)}" data-f="${f}" aria-label="${esc(`${role} · ${t(f)}`)}"><option value=""></option>${
    [1, 2, 3, 4, 5].map((v) => `<option ${punteggi[role]?.[f] === v ? "selected" : ""}>${v}</option>`).join("")}</select>`;
  $("griglia").innerHTML = `<tr><th class="l">${esc(t("hRuolo"))}</th><th>${esc(t("hLavoratori"))}</th>${CFG.factors.map((f) => `<th>${esc(t(f))}</th>`).join("")}<th>${esc(t("hPunti"))}</th><th class="l">${esc(t("hCategoria"))}</th></tr>` +
    rs.map(([role, n]) => {
      const p = valutato(role) ? points(punteggi[role], CFG) : null;
      return `<tr class="${p == null ? "todo" : ""}"><td class="l">${esc(role)}</td><td>${n}</td>${CFG.factors.map((f) => `<td>${sel(role, f)}</td>`).join("")}
        <td>${p ?? "–"}</td><td class="l">${p == null ? "–" : esc(bandFor(p, CFG))}</td></tr>`;
    }).join("");
  $("griglia").querySelectorAll("select").forEach((s) => s.addEventListener("change", () => {
    const { role, f } = s.dataset;
    punteggi[role] = { ...(punteggi[role] || {}), [f]: s.value ? Number(s.value) : undefined };
    store.set(K_GRIGLIA(), punteggi);
    nascondi();
    disegnaGriglia();
    pronto();
  }));
}

function pronto() {
  const f = files.paghe;
  $("esegui").disabled = !(f && !mancanti().length && (mapping.role || mapping.category)
    && (fonte() === "file" || ruoli().every(([r]) => valutato(r))));
}

$("scarica-griglia").addEventListener("click", () => {
  const rows = [[t("hRuolo"), t("hLavoratori"), ...CFG.factors.map((f) => t(f)), t("hPunti"), t("hCategoria")],
    ...ruoli().map(([role, n]) => {
      const s = punteggi[role] || {}, p = valutato(role) ? points(s, CFG) : "";
      return [role, n, ...CFG.factors.map((f) => s[f] ?? ""), p, p === "" ? "" : bandFor(p, CFG)];
    })];
  download(writeXlsx([{ name: t("x_griglia"), rows, widths: [30, 12, 14, 12, 16, 20, 10, 12] }]),
    `${i18n.lang === "it" ? "griglia_ruoli" : "job_evaluation"}.xlsx`, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
});

// ---- the assessment -----------------------------------------------------------------------------------------
const PAESI = { it: "IT", ita: "IT", italy: "IT", italia: "IT", pl: "PL", pol: "PL", poland: "PL", polska: "PL", polonia: "PL",
  de: "DE", deu: "DE", germany: "DE", deutschland: "DE", germania: "DE", es: "ES", esp: "ES", spain: "ES", espana: "ES", spagna: "ES",
  wlochy: "IT", italien: "IT", niemcy: "DE", alemania: "DE", allemagne: "DE", hiszpania: "ES", spanien: "ES", espagne: "ES",
  polen: "PL", pologne: "PL", italie: "IT" };
function paese(v) {
  const s = String(v ?? "").trim();
  const n = normalise(s);
  return PAESI[n] || PAESI[n.split("_")[0]] || s || $("paese").value;
}

function calcola() {
  try {
    messaggio("");
    const f = files.paghe, dc = f.decimalComma, mult = PERIODI[$("periodo").value], ore = Number($("ore").value);
    const roles = fonte() === "griglia" ? evaluate(ruoli().map(([role]) => ({ role, ...punteggi[role] })), CFG) : null;
    const cols = [...componenti];
    let esclusi = 0;
    const altri = {};
    const rows = [];
    f.rows.forEach((raw, i) => {
      const err = (e) => { throw new Error(t("eRiga", { r: i + 2, e })); };
      const g = generi[String(raw[mapping.gender] ?? "").trim()] || null;
      if (!g) {
        esclusi++;
        const c = mapping.country ? paese(raw[mapping.country]) : $("paese").value;
        altri[c] = (altri[c] || 0) + 1;
        return;
      }
      const num = (v) => { try { return number(v, dc); } catch { return err(t("eNumero", { e: v })); } };
      if (String(raw[mapping.base_pay] ?? "").trim() === "") err(t("ePaga"));
      let hours = ore;
      if (mapping.weekly_hours) hours = num(raw[mapping.weekly_hours]);
      else if (mapping.fte) { const x = num(raw[mapping.fte]); hours = (x > 1.5 ? x / 100 : x) * ore; }
      if (!(hours > 0)) err(t("eOre"));
      let category;
      if (roles) category = roles.get(String(raw[mapping.role] ?? "").trim())?.category ?? err(t("eRuolo", { r: raw[mapping.role] }));
      else category = String(raw[mapping.category] ?? "").trim() || err(t("eCategoria"));
      rows.push({ worker_id: String(raw[mapping.worker_id]), country: mapping.country ? paese(raw[mapping.country]) : $("paese").value,
        gender: g, category, role: mapping.role ? String(raw[mapping.role] ?? "").trim() : "",
        base_pay: num(raw[mapping.base_pay]) * mult, components: cols.map((c) => num(raw[c])), fixed: cols.map((c) => fisse.has(c)),
        weekly_hours: hours });
    });
    if (!rows.length) throw new Error(t("eVuoto"));
    const w = derive(rows, CFG);
    const noti = Object.keys(CFG.entities);
    const countries = [...noti.filter((c) => w.some((r) => r.country === c)), ...[...new Set(w.map((r) => r.country))].filter((c) => !noti.includes(c))];
    const ordine = categoryOrder(w, CFG);
    risultato = { w, countries, esclusi, items: byEntity(w, countries), screen: screen(w, countries, ordine, CFG),
      national: national(w, countries, CFG), nscreen: screen(w, countries, ordine, CFG, "national"), fisse: cols.filter((c) => fisse.has(c)),
      duties: obligations(w, countries, CFG, altri), roles, file: f.name, oggi: new Date().toISOString().slice(0, 10) };
    if (!countries.includes(entita) && !(entita === "Group" && countries.length > 1)) entita = countries[0];
    mostra();
    if (esclusi) messaggio(t("esclusi", { n: esclusi }), "info");
    $("risultati").scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  } catch (e) {
    messaggio(e.message);
  }
}
$("esegui").addEventListener("click", calcola);
["paese", "periodo", "ore"].forEach((id) => $(id).addEventListener("change", nascondi));
$("valuta").addEventListener("change", () => mostra());

// ---- results ------------------------------------------------------------------------------------------------
const nomePaese = (c) => L().paesi[c] || c;
// the sample employer's entities have site names; a client's file is named by country
const nomeEntita = (c) => (c === "Group" ? t("gruppo") : (esempio && CFG.entities[c]) || nomePaese(c));
const stato = (s) => ({ flag: t("sFlag"), ok: t("sOk"), one_sex: t("sOneSex") })[s];
const pill = (s) => `<span class="s-pill ${s === "flag" ? "is-high" : s === "ok" ? "is-ok" : "is-medium"}">${esc(stato(s))}</span>`;
const data = (iso) => (iso ? new Date(`${iso}T00:00:00`).toLocaleDateString(i18n.lang === "it" ? "it-IT" : "en-GB", { day: "numeric", month: "long", year: "numeric" }) : "–");
const fascia = (o) => (FASCE[i18n.lang] ? FASCE[i18n.lang][o.band] : [o.size_band, o.frequency]);
const righeEntita = () => risultato.screen.filter((r) => entita === "Group" || r.country === entita);
const chiaveGiust = (r) => `${r.country}|${r.category}`;

function mostra() {
  if (!risultato) return;
  const { countries, items, duties, esclusi } = risultato;
  $("risultati").style.display = "block";
  const scelte = countries.length > 1 ? [...countries, "Group"] : countries;
  $("entita").innerHTML = scelte.map((c) => `<button type="button" data-e="${esc(c)}" aria-pressed="${c === entita}">${esc(c === "Group" ? t("gruppo") : nomeEntita(c))}</button>`).join("");
  $("entita").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => { entita = b.dataset.e; mostra(); }));
  const it = items[entita], cats = righeEntita();
  const flag = cats.filter((r) => r.status === "flag");
  // small categories stay out of the total: with the other costs on show, it would give theirs away
  const costo = flag.filter((r) => !r.small_cell).reduce((s, r) => s + r.remedy_cost, 0);
  const fuori = flag.filter((r) => r.small_cell).length;
  $("kpis").innerHTML = [[t("kLavoratori"), i18n.number(it.workers), ""], [t("kDivario"), pct(it.a_mean_gap_hourly), Math.abs(it.a_mean_gap_hourly) >= CFG.threshold ? "is-bad" : "is-good"],
    [t("kCategorie"), `${flag.length} / ${cats.length}`, flag.length ? "is-bad" : "is-good"], [t("kCosto"), soldi(costo) + (fuori ? `<div class="note">${esc(t("notaCosto", { n: fuori }))}</div>` : ""), ""]]
    .map(([k, v, c]) => `<div class="s-kpi ${c}"><div class="k">${esc(k)}</div><div class="v">${v}</div></div>`).join("");
  $("stampa-meta").textContent = `${nomeEntita(entita)} · ${t("stampaMeta", { f: risultato.file, oggi: data(risultato.oggi), n: i18n.number(it.workers) })}`;

  $("tab-obblighi").innerHTML = `<tr><th class="l">${esc(t("hPaese"))}</th><th>${esc(t("hLavoratori"))}</th><th class="l">${esc(t("hFascia"))}</th><th class="l">${esc(t("hFrequenza"))}</th><th>${esc(t("hPrimo"))}</th><th>${esc(t("hRimedio"))}</th><th class="l">${esc(t("hStato"))}</th></tr>` +
    duties.map((o) => {
      const [fa, fr] = fascia(o), n = o.transposition;
      return `<tr><td class="l"><b>${esc(nomeEntita(o.country))}</b></td><td>${i18n.number(o.workers)}</td><td class="l">${esc(fa)}</td><td class="l">${esc(fr)}</td>
        <td>${data(o.first_report)}</td><td>${data(o.remedy_by)}</td>
        <td class="l">${n ? `${esc(L().statusT[n.status] || n.status)}<details class="naz"><summary>${esc(t("dettagli"))}</summary><p>${esc(n.instrument)}</p><p>${esc(n.reporting)}</p><p>${esc(n.notes)}</p><p class="note">${esc(t("xVerificato"))}: ${data(n.checked_on)}</p></details>`
          : esc(t("nonSeguito"))}</td></tr>`;
    }).join("");

  $("voci-sub").textContent = t("vociSub", { e: nomeEntita(entita), n: i18n.number(it.workers), d: i18n.number(it.women), u: i18n.number(it.men) });
  $("tab-voci").innerHTML = `<tr><th class="l">${esc(t("hVoce"))}</th><th>${esc(t("hValore"))}</th></tr>` +
    VOCI[i18n.lang].map(([k, label]) => `<tr><td class="l">${esc(label)}</td><td><b>${pct(it[k])}</b></td></tr>`).join("");
  $("grafico-quartili").innerHTML = graficoQuartili(it);
  $("grafico-categorie").innerHTML = graficoCategorie(cats);
  tabellaCategorie(cats);
  sezioneItalia();
}

// Italy's narrower measure, side by side with the Directive's, for an Italian employer.
function sezioneItalia() {
  const nat = risultato.national[entita];
  $("sez-italia").style.display = nat ? "block" : "none";
  if (!nat) return;
  const dir = risultato.items[entita];
  const diff = (a, b) => (a == null || b == null || Number.isNaN(a) || Number.isNaN(b) ? "–"
    : `${b >= a ? "+" : "−"}${i18n.number(Math.abs(b - a) * 100, 1)}`);
  const voci = VOCI[i18n.lang].filter(([k]) => /^(a_|c_)/.test(k))
    .concat([1, 2, 3, 4].map((q) => [`f_q${q}_share_women`, `(f) ${t("donne")} · ${t("quartile", { q })}`]));
  $("tab-italia-voci").innerHTML = `<tr><th class="l">${esc(t("hVoce"))}</th><th>${esc(t("hDirettiva"))}</th><th>${esc(t("hItalia"))}</th><th>${esc(t("hDiff"))}</th></tr>` +
    voci.map(([k, label]) => `<tr><td class="l">${esc(label)}</td><td>${pct(dir[k])}</td><td><b>${pct(nat[k])}</b></td><td>${diff(dir[k], nat[k])}</td></tr>`).join("");
  const dirRow = new Map(risultato.screen.filter((r) => r.country === entita).map((r) => [r.category, r]));
  const righe = risultato.nscreen.filter((r) => r.country === entita);
  const lock = `<span class="lock">🔒 ${esc(t("riservato"))}</span>`;
  $("tab-italia-cat").innerHTML = `<tr><th class="l">${esc(t("hCategoria"))}</th><th>${esc(t("donne"))}</th><th>${esc(t("uomini"))}</th>
    <th>${esc(t("hDivOrario"))}</th><th>${esc(t("hDivAnnuo"))}</th><th class="l">${esc(t("hEsitoIt"))}</th><th class="l">${esc(t("hEsitoDir"))}</th><th>${esc(t("hCosto"))}</th></tr>` +
    righe.map((r) => { const d = dirRow.get(r.category) || {};
      return `<tr><td class="l"><b>${esc(r.category)}</b></td><td>${r.women}</td><td>${r.men}</td>
        ${r.small_cell ? `<td>${lock}</td><td>${lock}</td>` : `<td><b>${pct(r.gap_hourly)}</b></td><td>${pct(r.gap_annual)}</td>`}
        <td class="l">${pill(r.status)}</td><td class="l">${d.status ? pill(d.status) : "–"}</td>
        <td>${r.status !== "flag" ? "–" : r.small_cell ? lock : soldi(r.remedy_cost)}</td></tr>`; }).join("");
  const cambiano = righe.filter((r) => dirRow.get(r.category)?.status !== r.status).length;
  const f = risultato.fisse;
  $("nota-italia").textContent = `${cambiano ? t("italiaCambia", { n: cambiano }) : t("italiaUguale")} ${f.length ? t("italiaFisse", { c: f.join(", ") }) : t("italiaSoloBase")}`;
}

function graficoQuartili(it) {
  const W = 720, row = 40, lab = 150, H = row * 4 + 8, bw = W - lab - 10;
  const bars = [1, 2, 3, 4].map((q, i) => {
    const d = it[`f_q${q}_share_women`] || 0, y = i * row + 6, wd = d * bw;
    const edge = q === 1 ? ` · ${t("qBassa")}` : q === 4 ? ` · ${t("qAlta")}` : "";
    return `<text x="0" y="${y + 20}" class="lab">${esc(t("quartile", { q }) + edge)}</text>
      <rect x="${lab}" y="${y}" width="${wd}" height="28" rx="6" fill="var(--women)"/>
      <rect x="${lab + wd}" y="${y}" width="${bw - wd}" height="28" rx="6" fill="var(--men)"/>
      ${d > 0.12 ? `<text x="${lab + 8}" y="${y + 19}" style="fill:#fff;font-weight:600">${pct(d)}</text>` : ""}
      ${1 - d > 0.12 ? `<text x="${lab + bw - 8}" y="${y + 19}" text-anchor="end" style="fill:#fff;font-weight:600">${pct(1 - d)}</text>` : ""}`;
  }).join("");
  return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(t("quartili"))}">${bars}</svg>`;
}

function graficoCategorie(cats) {
  const rows = cats.filter((r) => r.status !== "one_sex" && !r.small_cell);
  if (!rows.length) return "";
  const W = 720, row = 30, lab = entita === "Group" ? 170 : 110, H = rows.length * row + 30, right = 64;
  const max = Math.max(0.1, ...rows.map((r) => Math.abs(r.gap_hourly))) * 1.05;
  const x0 = lab + (W - lab - right) / 2, sc = (W - lab - right) / 2 / max;
  const th = CFG.threshold * sc;
  const bars = rows.map((r, i) => {
    const y = i * row + 24, v = r.gap_hourly, wd = Math.abs(v) * sc, x = v >= 0 ? x0 : x0 - wd;
    const name = entita === "Group" ? `${r.country} · ${r.category}` : r.category;
    const tx = v >= 0 ? x0 + wd + 6 : x0 - wd - 6;
    return `<text x="0" y="${y + 15}" class="lab">${esc(name)}</text>
      <rect x="${x}" y="${y + 2}" width="${Math.max(wd, 1)}" height="20" rx="4" fill="${r.status === "flag" ? "var(--bad)" : "var(--women)"}"/>
      <text x="${tx}" y="${y + 16}" text-anchor="${v >= 0 ? "start" : "end"}">${pct(v)}</text>`;
  }).join("");
  const axis = `<line x1="${x0}" x2="${x0}" y1="16" y2="${H}" stroke="var(--line)"/>
    <line x1="${x0 + th}" x2="${x0 + th}" y1="16" y2="${H}" stroke="var(--muted)" stroke-dasharray="4 4"/>
    <line x1="${x0 - th}" x2="${x0 - th}" y1="16" y2="${H}" stroke="var(--muted)" stroke-dasharray="4 4"/>
    <text x="${x0 + th}" y="11" text-anchor="middle">+${i18n.percent(CFG.threshold, 0)}</text>
    <text x="${x0 - th}" y="11" text-anchor="middle">−${i18n.percent(CFG.threshold, 0)}</text>`;
  return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(t("categorie"))}">${axis}${bars}</svg>`;
}

function tabellaCategorie(cats) {
  const giust = store.get(K_GIUST(), {});
  const ora = (x) => soldi(x, 2);
  const lock = `<span class="lock">🔒 ${esc(t("riservato"))}</span>`;
  $("tab-categorie").innerHTML = `<tr>${entita === "Group" ? `<th class="l">${esc(t("hPaese"))}</th>` : ""}<th class="l">${esc(t("hCategoria"))}</th><th>${esc(t("donne"))}</th><th>${esc(t("uomini"))}</th>
    <th>${esc(t("hMediaD"))}</th><th>${esc(t("hMediaU"))}</th><th>${esc(t("hDivBase"))}</th><th>${esc(t("hDivComp"))}</th><th>${esc(t("hDivOrario"))}</th><th>${esc(t("hDivAnnuo"))}</th>
    <th class="l">${esc(t("hEsito"))}</th><th>${esc(t("hCosto"))}</th></tr>` +
    cats.map((r) => {
      const k = chiaveGiust(r), testo = giust[k] || "";
      return `<tr>${entita === "Group" ? `<td class="l">${esc(r.country)}</td>` : ""}<td class="l"><b>${esc(r.category)}</b></td><td>${r.women}</td><td>${r.men}</td>
      <td>${r.small_cell ? lock : ora(r.hourly_total_women)}</td><td>${r.small_cell ? lock : ora(r.hourly_total_men)}</td>
      ${r.small_cell ? `<td>${lock}</td><td>${lock}</td><td>${lock}</td><td>${lock}</td>`
        : `<td>${pct(r.gap_base)}</td><td>${pct(r.gap_components)}</td><td><b>${pct(r.gap_hourly)}</b></td><td>${pct(r.gap_annual)}</td>`}<td class="l">${pill(r.status)}</td>
      <td>${r.status !== "flag" ? "–" : r.small_cell ? lock : soldi(r.remedy_cost)}</td></tr>${r.status !== "flag" ? ""
        : `<tr class="giust-row"><td class="l" colspan="${entita === "Group" ? 12 : 11}"><label class="s-why" for="g-${esc(k)}">${esc(t("hGiust"))} · ${esc(r.category)}</label>
        <textarea class="giust" id="g-${esc(k)}" data-k="${esc(k)}" placeholder="${esc(t("giustPh"))}">${esc(testo)}</textarea><div class="giust-print">${esc(testo)}</div></td></tr>`}`;
    }).join("");
  $("tab-categorie").querySelectorAll("textarea").forEach((a) => a.addEventListener("input", () => {
    const g = store.get(K_GIUST(), {});
    g[a.dataset.k] = a.value;
    store.set(K_GIUST(), g);
    a.nextElementSibling.textContent = a.value;
  }));
  const piccole = cats.filter((r) => r.small_cell).length;
  $("nota-piccole").textContent = piccole ? t("notaPiccole", { n: piccole, m: CFG.min_cell }) : "";
}
$("stampa").addEventListener("click", () => print());

$("scarica-xlsx").addEventListener("click", () => {
  const { countries, items, screen: s, duties, roles, w, esclusi } = risultato;
  const giust = store.get(K_GIUST(), {});
  const p100 = (x) => (x == null || Number.isNaN(x) ? "" : Math.round(x * 10000) / 100);
  const entities = countries.length > 1 ? [...countries, "Group"] : countries;
  const sintesi = [[`${t("hVoce")} (${t("xPct")})`, ...entities.map(nomeEntita)],
    [t("kLavoratori"), ...entities.map((e) => items[e].workers)], [t("donne"), ...entities.map((e) => items[e].women)],
    [t("uomini"), ...entities.map((e) => items[e].men)],
    ...VOCI[i18n.lang].map(([k, label]) => [label, ...entities.map((e) => p100(items[e][k]))]),
    ...[1, 2, 3, 4].flatMap((q) => [[`(f) ${t("donne")} · ${t("quartile", { q })}`, ...entities.map((e) => p100(items[e][`f_q${q}_share_women`]))],
      [`(f) ${t("uomini")} · ${t("quartile", { q })}`, ...entities.map((e) => p100(items[e][`f_q${q}_share_men`]))]])];
  const remedy = Object.fromEntries(duties.map((o) => [o.country, o.remedy_by]));
  const categorieX = [[t("hPaese"), t("hCategoria"), t("donne"), t("uomini"), t("xMediaD"), t("xMediaU"), `${t("hDivBase")} (%)`, `${t("hDivComp")} (%)`,
    `${t("hDivOrario")} (%)`, `${t("hDivAnnuo")} (%)`, t("hEsito"), t("hCosto"), t("hGiust"), t("xResponsabile"), t("xEntro")],
    ...s.map((r) => [nomeEntita(r.country), r.category, r.women, r.men, r.small_cell ? t("riservato") : Math.round(r.hourly_total_women * 100) / 100,
      r.small_cell ? t("riservato") : Math.round(r.hourly_total_men * 100) / 100,
      ...(r.small_cell ? Array(4).fill(t("riservato")) : [p100(r.gap_base), p100(r.gap_components), p100(r.gap_hourly), p100(r.gap_annual)]),
      stato(r.status), r.status !== "flag" ? "" : r.small_cell ? t("riservato") : Math.round(r.remedy_cost),
      giust[chiaveGiust(r)] || "", "", r.status === "flag" ? remedy[r.country] || "" : ""])];
  const obblighi = [[t("hPaese"), t("hLavoratori"), t("hFascia"), t("hFrequenza"), t("hPrimo"), t("hRimedio"), t("hStato"), t("xIstituto"), t("xNote"), t("xVerificato")],
    ...duties.map((o) => { const [fa, fr] = fascia(o), n = o.transposition || {};
      return [nomeEntita(o.country), o.workers, fa, fr, o.first_report || "", o.remedy_by || "", n.status ? L().statusT[n.status] || n.status : t("nonSeguito"),
        n.instrument || "", n.notes || "", n.checked_on || ""]; })];
  const sheets = [
    { name: t("x_sintesi"), rows: sintesi, widths: [70, ...entities.map(() => 18)] },
    { name: t("x_categorie"), rows: categorieX, widths: [18, 12, 9, 9, 16, 16, 14, 16, 14, 14, 20, 14, 50, 18, 14] },
    { name: t("x_obblighi"), rows: obblighi, widths: [18, 12, 16, 22, 14, 18, 20, 50, 60, 14] },
  ];
  for (const [c, nat] of Object.entries(risultato.national)) {
    const dir = items[c];
    const voci = VOCI[i18n.lang].filter(([k]) => /^(a_|c_)/.test(k))
      .concat([1, 2, 3, 4].map((q) => [`f_q${q}_share_women`, `(f) ${t("donne")} · ${t("quartile", { q })}`]));
    const dirStato = new Map(s.filter((r) => r.country === c).map((r) => [r.category, r.status]));
    sheets.push({ name: Object.keys(risultato.national).length > 1 ? `${t("x_italia")} ${c}` : t("x_italia"), rows: [
      [`${t("hVoce")} (${t("xPct")})`, t("hDirettiva"), t("hItalia")],
      ...voci.map(([k, label]) => [label, p100(dir[k]), p100(nat[k])]), [],
      [t("hCategoria"), t("donne"), t("uomini"), `${t("hDivOrario")} (%)`, `${t("hDivAnnuo")} (%)`, t("hEsitoIt"), t("hEsitoDir"), t("hCosto")],
      ...risultato.nscreen.filter((r) => r.country === c).map((r) => [r.category, r.women, r.men,
        r.small_cell ? t("riservato") : p100(r.gap_hourly), r.small_cell ? t("riservato") : p100(r.gap_annual), stato(r.status),
        stato(dirStato.get(r.category)), r.status !== "flag" ? "" : r.small_cell ? t("riservato") : Math.round(r.remedy_cost)]),
      [], [risultato.fisse.length ? t("italiaFisse", { c: risultato.fisse.join(", ") }) : t("italiaSoloBase")]],
      widths: [60, 22, 22, 14, 14, 20, 20, 14] });
  }
  if (roles) {
    const n = new Map();
    w.forEach((r) => n.set(r.role, (n.get(r.role) || 0) + 1));
    sheets.push({ name: t("x_griglia"), rows: [[t("hRuolo"), t("hLavoratori"), ...CFG.factors.map((f) => t(f)), t("hPunti"), t("hCategoria")],
      ...[...roles].map(([role, v]) => [role, n.get(role) || 0, ...CFG.factors.map((f) => punteggi[role][f]), v.points, v.category])],
      widths: [30, 12, 14, 12, 16, 20, 10, 12] });
  }
  sheets.push({ name: t("x_impostazioni"), rows: [[t("x_impostazioni"), ""], [t("xFile"), risultato.file], [t("xData"), risultato.oggi],
    [t("xPeriodo"), t($("periodo").value)], [t("xOre"), Number($("ore").value)], [t("xSoglia"), i18n.percent(CFG.threshold, 0)],
    [t("xMinimo"), CFG.min_cell], [t("xEsclusi"), esclusi], [t("valuta"), $("valuta").value || "—"], [t("xFonte"), "https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/blob/main/docs/method.md"]],
    widths: [44, 70] });
  download(writeXlsx(sheets), `${i18n.lang === "it" ? "verifica_divario" : "pay_gap_assessment"}_${risultato.oggi}.xlsx`,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
});

i18n.apply();
i18n.onChange(() => {
  opzioni();
  if (files.paghe) { disegnaMappa(false); disegnaFisse(); categorie(); }
  mostra();
});

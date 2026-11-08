# Contratto dati per il pilot italiano

## Scopo

Questo tracciato serve a una prima analisi delle retribuzioni di un solo datore di lavoro italiano. Non è un file di trasmissione ufficiale né una certificazione di conformità. Il pilot usa importi effettivamente pagati fra il 1° gennaio e il 31 dicembre dell’anno selezionato; per una simulazione annualizzata usare solo dati dimostrativi.

La Direttiva (UE) 2023/970 definisce il livello retributivo come retribuzione lorda annua e corrispondente retribuzione lorda oraria. Il calcolo orario di questa versione è una scelta tecnica da validare con HR e consulenza del lavoro prima di qualsiasi uso legale: [EUR-Lex, articolo 3 e considerando 22](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023L0970).

## Formato minimo

Usare un file Excel (.xlsx) o CSV, una riga per lavoratore e nessuna riga di totale. L’importazione avviene nella pagina del browser.

| Campo | Richiesto | Contenuto |
|---|---:|---|
| worker_id | sì | Identificativo casuale e univoco nel file, ad esempio W0001. Non inserire nome, matricola aziendale, codice fiscale o e-mail. |
| gender | sì | Codice concordato con HR e verificato nella schermata di mappatura. Questa versione confronta solo i codici mappati come donna o uomo; gli altri valori restano fuori dai confronti, pur contando nel numero di lavoratori. |
| base_pay | sì | Retribuzione base lorda effettivamente pagata nell’intero anno civile selezionato, nella valuta del datore di lavoro. Non inserire RAL contrattuale o mensilità da moltiplicare in modalità pagamenti effettivi. |
| annual_hours | sì per pagamenti effettivi | Ore contrattuali totali per lavoratore nell’anno civile selezionato, coerenti con il periodo di retribuzione pagato. |
| weekly_hours | no | Media settimanale facoltativa come contesto. Non entra nel calcolo quando annual_hours è presente e non viene confrontata automaticamente con il totale annuo. |
| category oppure role | almeno uno | Categoria di pari valore già verificata, oppure ruolo da usare nella griglia esplorativa. In Italia partire dalla classificazione applicabile del CCNL. |
| country | no | Codice paese del datore di lavoro; per questo pilot usare IT. Se assente, indicare il paese nelle impostazioni. |
| componenti retributive | se presenti | Una colonna numerica per componente, con gli importi lordi effettivamente pagati nello stesso anno di base_pay. Non includere costi datoriali. |

Valori monetari e ore devono essere numerici, senza totali per persona duplicati. Un file pilota italiano deve usare EUR. Se si caricano componenti, distinguere quelle fisse e continuative pagate per regola generale da bonus, provvigioni, importi personali o una tantum; la selezione delle componenti incide sul confronto nazionale italiano e va confermata con HR/consulenza del lavoro.

## Limite del denominatore orario

In modalità pagamenti effettivi, la pagina richiede annual_hours e usa le ore contrattuali totali mappate per ciascun lavoratore come denominatore del dato orario. Se sono forniti entrambi, il calcolo usa annual_hours; weekly_hours è soltanto contesto facoltativo e non viene confrontata automaticamente con il totale annuo. Verificare con HR che le ore coprano lo stesso periodo degli importi pagati, incluse eventuali assunzioni, cessazioni, periodi non retribuiti o variazioni d’orario. La definizione nazionale e l’uso legale del denominatore richiedono ancora una verifica specialistica.

La griglia di valutazione dei ruoli è esplorativa: i punteggi non stabiliscono automaticamente categorie legali. Per il pilot usare una categoria fornita e approvata dall’azienda; in Italia verificare il livello CCNL applicabile.

## Non includere

Non inserire nomi, matricole reali, codici fiscali, indirizzi, e-mail, IBAN, data di nascita, diagnosi, assenze mediche, valutazioni individuali, performance rating, note dei manager, risultati di survey o dati non necessari al confronto.

Un identificativo pseudonimo resta dato personale se l’azienda può ricondurlo a una persona. Il cliente deve approvare finalità, base giuridica, accessi, informativa, retention e necessità della DPIA con il proprio DPO o consulente privacy prima di usare dati reali.

## Trattamento locale e chiusura della sessione

- La pagina legge i file con l’API File del browser; non invia il file paghe al server.
- Le righe, i punteggi dei ruoli, le giustificazioni e le mappature restano nella memoria della pagina fino alla cancellazione o al ricaricamento.
- La scelta della lingua è l’unico dato salvato in localStorage.
- Il pulsante “Svuota file e dati di lavoro” azzera i dati e le impostazioni della sessione. Chiudere la scheda al termine.
- Il report non riporta il nome originale del file. L’Excel scaricato resta comunque un documento aziendale riservato: conservarlo solo in una posizione autorizzata e cancellare eventuali copie di lavoro secondo le regole del cliente.

## Controlli prima dell’importazione

1. Confermare datore di lavoro, anno e valuta con HR/Compensation.
2. Verificare che base_pay e ogni componente siano somme effettivamente pagate fra il 1° gennaio e il 31 dicembre dello stesso anno.
3. Rimuovere identificativi diretti e colonne estranee.
4. Verificare che worker_id sia univoco e che ogni persona compaia una sola volta.
5. Controllare codici di genere, importi negativi/anomali e ore annue; trattare l’eventuale media settimanale come dato di contesto.
6. Confermare le categorie con HR e rappresentanti dei lavoratori; per l’Italia partire dal CCNL.
7. Riconciliare un campione di righe e i totali aggregati con l’export sorgente prima di discutere i risultati.

Non caricare il file reale in GitHub, issue, pull request, email o strumenti di assistenza. Condividere soltanto dati sintetici o aggregati approvati.

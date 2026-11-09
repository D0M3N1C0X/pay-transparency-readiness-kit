# Runbook per il pilot italiano

## Obiettivo e limiti

Validare con un datore di lavoro il flusso locale di importazione, la mappatura dei codici paga, la riconciliazione con il totale lordo annuo e la leggibilità del report. È una verifica preliminare di prodotto, non un parere legale né una certificazione di conformità.

Usare dati sintetici per le prove tecniche. I dati reali restano sul dispositivo autorizzato dell’azienda e non vanno inviati al fondatore, caricati su GitHub o inseriti in issue, email o strumenti di assistenza.

## Ruoli da concordare

| Ruolo | Responsabilità nel pilot |
|---|---|
| HR / Compensation | Definisce periodo, valuta, componenti, codici paga e classificazioni; approva le categorie di lavoratori. |
| Referente paghe | Produce l’export e conferma che ore e importi coprano lo stesso anno civile. |
| DPO / Privacy / Legal del cliente | Conferma finalità, base giuridica, informativa, accessi, retention e necessità della DPIA prima di usare dati reali. |
| Operatore del pilot | Avvia la pagina sul dispositivo autorizzato, esegue il flusso e cancella i dati temporanei a fine sessione. |

## Preparazione dell’export

1. Concordare il datore di lavoro italiano, EUR e un anno civile concluso.
2. Preparare una riga per lavoratore, senza righe di totale. Usare un ID casuale e univoco, non riconducibile dal fondatore alla persona.
3. Esportare base_pay come somma lorda effettivamente pagata nell’anno; aggiungere payroll_total come colonna separata con il lordo annuo pagato dalla fonte paghe.
4. Esportare annual_hours come ore contrattuali totali individuali nello stesso anno. weekly_hours può essere aggiunta come dato di contesto.
5. Tenere un codice paga per colonna. Preparare una mappa uno-a-uno con pay_code, intestazione identica all’export, descrizione e classificazione HR: fixed_continuing, variable o one_off.
6. Rimuovere nome, matricola reale, codice fiscale, email, IBAN, data di nascita e colonne non necessarie. Non esportare dati sanitari, note, valutazioni individuali o risultati di survey.
7. Usare una categoria già approvata da HR; per l’Italia verificare il livello CCNL applicabile. Non usare la griglia esplorativa come classificazione legale.

Modelli: [export paghe sintetico](../web/template_payroll.csv), [mappa codici paga di esempio](../web/template_pay_code_map.csv) e [contratto dati](pilot-data-contract.md). Le classificazioni dei modelli sono illustrative e devono essere sostituite o confermate dall’azienda.

## Sessione guidata

1. Aprire il browser sul dispositivo autorizzato e provare prima i file sintetici. Verificare che la pagina non mostri errori e che il report si scarichi.
2. Caricare localmente l’export paghe approvato. Abbinare le colonne, inclusi totale lordo e ore annue; risolvere le intestazioni ambigue con una scelta esplicita.
3. Se manca la mappa, scaricare la bozza precompilata dall’app. Contiene le intestazioni numeriche esatte, non i valori paghe. Eliminare le colonne non retributive e completare codici, descrizioni e classificazioni con HR; poi caricare il file completato.
4. Verificare che ogni voce inclusa sia classificata una volta sola e che il totale separato copra base e componenti selezionate. Le componenti non mappate non vanno trattate come se fossero comprese.
5. Selezionare i pagamenti effettivi e l’anno corretto, eseguire l’analisi e controllare il riepilogo della riconciliazione. Il controllo include anche chi non è confrontato per genere. Gli scarti sono diagnostici e non bloccano il report.
6. Esaminare il dettaglio per categoria. I gruppi piccoli o già protetti dal controllo del divario restano nascosti.
7. HR verifica categorie e risultati aggregati. Solo dopo l’approvazione, scaricare il report Excel; conservarlo come dato aziendale riservato.
8. Usare “Svuota file e dati di lavoro”, poi ricaricare o chiudere la scheda. Gestire il file scaricato secondo le regole di retention del cliente.

## Criteri di uscita

Il pilot è pronto per una valutazione HR quando:

- il file contiene una riga per persona, ID pseudonimi univoci, anno e valuta concordati;
- ore, base, componenti e totale coprono lo stesso periodo;
- le voci di paga sono mappate senza duplicati e classificate da HR;
- importi mancanti o non validi sono risolti oppure documentati;
- ogni scarto oltre la tolleranza ha una spiegazione approvata da HR/Compensation;
- le categorie sono state confermate dall’azienda e le soppressioni dei gruppi piccoli sono accettate;
- il cliente ha deciso chi può accedere all’export e quando eliminarlo.

Nel verbale del pilot registrare solo esito, numero complessivo di righe, conteggi aggregati di riconciliazione, problemi risolti e azioni aperte. Non annotare ID, importi individuali o dettagli che permettano di ricostruire una retribuzione.

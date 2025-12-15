# Road-hazard-map 🇬🇧

My thesis project: Comparison of LLM and Transformer models for the classification of newspaper articles regarding road accidents. 
---

## Project Overview

This project investigates the use of Large Language Models (LLMs) for the automatic analysis of newspaper articles related to road accidents, with the goal of transforming unstructured textual data into structured information for road safety analysis.

## Objectives

The first objective is to evaluate the effectiveness of **Qwen3 – 4B Instruct** as a multi-label classification model, comparing it with a fine-tuned Transformer-based model (**Italian BERT XXL**).  
The second objective is to build a road risk index map for the municipality of Parma, using data extracted from journalistic sources and comparing the results with official OpenData provided by local authorities.

## Methodology

The experimental workflow is divided into three main phases:
1. **Prompt engineering**, aimed at improving the performance and stability of the LLM.
2. **Model comparison**, assessing whether a relatively small, non-task-specific LLM can approach the performance of a fine-tuned Transformer model.
3. **Territorial analysis pipeline**, including newspaper scraping, sentence-level classification, geolocation through NER and Nominatim, and computation of a grid-based road risk index.

## Conclusions

This work demonstrates that the integration of NLP techniques, geolocation, and statistical analysis enables the extraction of latent knowledge from unstructured news articles. With further refinements, this approach may support alternative and complementary tools for monitoring road safety and planning targeted interventions.

---
---
---

# Mappa di pericolosità stradale  🇮🇹 

**Il mio progetto di tesi: # Confronto di modelli LLM e Transformer per la classificazione di articoli di giornale riguardanti incidenti stradali.
** 
---

## Panoramica del progetto 

Questo repository contiene un progetto di ricerca sull’utilizzo dei Large Language Model (LLM) per l’analisi automatica di articoli giornalistici relativi a incidenti stradali, con l’obiettivo di trasformare testi non strutturati in dati utili per l’analisi della sicurezza stradale.

## Obiettivi

Il primo obiettivo è valutare l’efficacia di **Qwen3 – 4B Instruct** come modello di classificazione multi-etichetta, confrontandolo con un modello fine-tuned (**Italian BERT XXL**).  
Il secondo obiettivo è la costruzione di una mappa dell’indice di pericolosità stradale del comune di Parma, basata su dati estratti da articoli di giornale e confrontata con gli OpenData ufficiali.

## Metodologia

Il lavoro si articola in tre fasi principali:
1. **Prompt engineering** per ottimizzare le prestazioni di Qwen.
2. **Confronto tra modelli** LLM e Transformer fine-tuned per la classificazione frase per frase.
3. **Pipeline di analisi territoriale**, comprendente scraping degli articoli, classificazione automatica, geolocalizzazione tramite NER e Nominatim, e calcolo dell’indice di pericolosità su griglia geografica.

## Conclusioni

Il progetto dimostra come l’integrazione di NLP, geolocalizzazione e analisi statistica consenta di estrarre conoscenza latente da articoli di cronaca, offrendo un supporto informativo potenzialmente utile per il monitoraggio della sicurezza stradale.

---
title: "Quarterly GDP forecasting under short data histories and mixed-frequency information: An application to Benin"
summary: Comparaison d’une prévision directe et d’une agrégation sectorielle du PIB trimestriel du Bénin lorsque les historiques sont courts et les indicateurs de fréquences différentes.
authors: "Aristide Médénou · Massavo Emmanuel Abed-N. Salako"
year: 2026
date: 2026-07-01
publication_type: Manuscrit de recherche appliquée
search_terms: prévision PIB Bénin prévision économique historique court données mixtes MIDAS modèles macroéconomie composantes sectorielles rétropolation
comment_term: publication-prevision-pib-benin
full_text_note: Le texte intégral n’est pas proposé sur le site. Cette fiche en présente le résumé, la méthode et les principaux résultats.
---
## Résumé

Cette étude examine la prévision du PIB trimestriel lorsque les historiques sont courts et que l’information est disponible à des fréquences différentes, en prenant le Bénin comme étude de cas d’un problème institutionnel plus large rencontré par les économies où les données sont contraintes. Elle compare une prévision issue d’un modèle unique estimé au niveau agrégé à une stratégie par composantes qui prévoit séparément les valeurs ajoutées primaire, secondaire et tertiaire ainsi que les impôts nets, avant agrégation.

Les deux stratégies sont évaluées par validation roulante hors échantillon sur des dates de prévision communes. Les résultats montrent que l’agrégation sectorielle produit les prévisions les plus précises, particulièrement aux horizons longs. Les indicateurs utiles diffèrent également selon les branches : la saisonnalité domine dans le primaire ; les indicateurs industriels et monétaires comptent dans le secondaire ; la dynamique récente, les taux d’intérêt et l’activité des services informent le tertiaire ; enfin, les impôts nets deviennent plus étroitement liés à la masse monétaire M2 au-delà du très court terme. Une rétropolation trimestrielle sous contrainte annuelle prolonge aussi la série historique d’une manière cohérente avec les comptes nationaux.

## Question et contribution

L’étude demande si une institution disposant d’un historique trimestriel récent et d’indicateurs fragmentés peut améliorer sa prévision du PIB en respectant sa structure de production. L’architecture sectorielle repose sur l’identité comptable :

$$
Y_t = VA_{P,t} + VA_{S,t} + VA_{T,t} + TAX_t,
$$

où les trois valeurs ajoutées correspondent aux secteurs primaire, secondaire et tertiaire, et où \\(TAX_t\\) désigne les impôts nets sur les produits. La contribution est à la fois empirique et opérationnelle : comparer les deux stratégies sur des dates strictement identiques, puis identifier une organisation de prévision parcimonieuse, interprétable et cohérente avec les comptes nationaux.

## Données et méthode

L’application mobilise les comptes nationaux trimestriels du Bénin de 2017T1 à 2025T2, soit 34 trimestres, ainsi que des indicateurs d’activité, de prix, de commerce extérieur, de monnaie, de crédit, de taux d’intérêt, de change, de matières premières et de pluviométrie. Les séries annuelles de PIB utilisées pour contraindre la rétropolation couvrent la période 2005-2024.

Les familles de modèles restent volontairement sobres : saisonnalité, modèles autorégressifs AR(1) et AR(2), régressions avec indicateurs, U-MIDAS pour intégrer explicitement l’information mensuelle et régression ridge lorsque le nombre de variables augmente. Les prévisions sont produites à un, deux, trois et quatre trimestres, puis évaluées par validation roulante hors échantillon avec le RMSE et la MAE. La comparaison finale est réalisée sur un échantillon commun à chaque horizon afin que l’écart de performance provienne de la stratégie et non de dates d’évaluation différentes.

## Résultats clés

L’agrégation sectorielle réduit l’erreur de prévision du taux de croissance à chacun des quatre horizons :

| Horizon | RMSE sectoriel | RMSE direct | Gain relatif du RMSE |
| --- | ---: | ---: | ---: |
| 1 trimestre | 2,01 | 2,13 | 5 % |
| 2 trimestres | 1,85 | 2,12 | 12 % |
| 3 trimestres | 1,84 | 1,88 | 2 % |
| 4 trimestres | 1,41 | 1,78 | 21 % |

L’avantage est particulièrement net à quatre trimestres : le RMSE en niveau passe de 50,63 à 39,61 milliards de francs CFA constants et la MAE de 40,00 à 32,99 milliards. Les modèles retenus révèlent en outre une structure économique différenciée :

- dans le primaire, les dynamiques récentes et la saisonnalité trimestrielle suffisent largement ;
- dans le secondaire, l’IPI et l’IPPI sont complétés par le taux débiteur ou M2 selon l’horizon ;
- dans le tertiaire, les retards de croissance, le taux débiteur et l’indice du chiffre d’affaires des services sont les plus informatifs ;
- pour les impôts nets, la saisonnalité domine à un trimestre, puis M2 intervient de deux à quatre trimestres.

La rétropolation utilise la méthode de Denton-Cholette pour distribuer les totaux annuels entre les trimestres tout en respectant exactement la contrainte annuelle. Sur la période de recouvrement 2017-2024, elle fournit une trajectoire historique cohérente, avec une MAE de 3,30 points de croissance et de 102,97 milliards de francs CFA en niveau. Cette série complète l’analyse historique ; elle ne remplace pas les comptes trimestriels observés.

## Portée et limites

Les résultats restent liés au cas béninois et à un échantillon trimestriel encore court. Ils ne constituent donc pas une supériorité universelle de l’agrégation sectorielle. Les prolongements prioritaires sont d’enrichir l’information antérieure à 2017, notamment avec des indicateurs sectoriels, budgétaires, énergétiques, portuaires, de transport et d’agriculture, puis d’évaluer les modèles dans des conditions reproduisant plus finement les calendriers réels de publication. Des modèles multivariés plus riches deviendront pertinents à mesure que l’historique s’allongera.

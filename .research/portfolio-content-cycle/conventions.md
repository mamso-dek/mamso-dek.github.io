# Conventions de coût et stratégie de Leland

## Convention du projet

Le coût payé lors d’une variation de position \(\Delta h_t\) est

\[
\text{coût}_t=c\,S_t|\Delta h_t|,
\]

où \(c\) est un coût **aller simple** par unité de notionnel. Une ouverture et une fermeture de même taille coûtent donc approximativement \(2c\) fois le notionnel si le prix reste inchangé. La liquidation terminale est incluse.

## Passage à la convention de Leland

Une présentation courante de Leland note \(C\) le coût aller-retour et facture \(C|\Delta h|S/2\) à chaque transaction. Dans notre convention,

\[
C=2c.
\]

Pour un call convexe, la variance ajustée est

\[
\sigma_L^2=\sigma^2\left(1+\sqrt{\frac{2}{\pi}}\frac{C}{\sigma\sqrt{\Delta t}}\right),
\]

soit, avec le coût aller simple \(c\),

\[
\sigma_L
=\sigma\sqrt{1+\sqrt{\frac{8}{\pi}}\frac{c}{\sigma\sqrt{\Delta t}}}.
\]

La stratégie de référence utilisera la delta Black–Scholes calculée avec \(\sigma_L\). Sa prime initiale sera cependant traitée avec prudence : pour comparer uniquement les politiques de couverture, toutes les stratégies d’une expérience partiront de la même prime. Une analyse séparée pourra montrer le prix ajusté de Leland, mais ne le mélangera pas avec la comparaison à prime commune.

## Limites

- L’ajustement est une approximation asymptotique fondée sur de petits coûts et un petit pas de temps.
- La formule dépend de la convention de coût ; omettre le facteur deux change matériellement le benchmark.
- Elle ne constitue pas une stratégie optimale universelle sous frictions.
- Elle sera présentée comme une référence classique, non comme une vérité de marché.

Référence principale : Hayne E. Leland, « Option Pricing and Replication with Transactions Costs », *The Journal of Finance*, 40(5), 1985, DOI [10.1111/j.1540-6261.1985.tb02383.x](https://doi.org/10.1111/j.1540-6261.1985.tb02383.x).

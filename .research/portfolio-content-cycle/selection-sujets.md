# Sélection du sujet

Date de décision : 1er septembre 2026.

## Critères et pondérations

Chaque critère est noté de 1 à 5. Le score final est une moyenne pondérée.

| Critère | Poids | Question posée |
| --- | ---: | --- |
| Pertinence scientifique | 20 % | La question mobilise-t-elle une modélisation défendable et des comparaisons non triviales ? |
| Intérêt professionnel | 20 % | Le travail montre-t-il des compétences recherchées en finance quantitative ou gestion des risques ? |
| Données et reproductibilité | 15 % | Les données sont-elles accessibles, licites et suffisantes pour une évaluation reproductible ? |
| Littérature accessible | 10 % | Les références originales nécessaires sont-elles identifiables et vérifiables ? |
| Potentiel de visualisation | 10 % | Le résultat peut-il être expliqué par des figures et diagnostics informatifs ? |
| Faisabilité en cinq jours | 15 % | Les calculs, contrôles et livrables peuvent-ils être correctement terminés ? |
| Complémentarité | 10 % | Le sujet ajoute-t-il une compétence sans répéter les travaux déjà présents ? |

## Candidats

### A. Couverture neuronale sous coûts de transaction

**Question envisagée.** Une politique de couverture apprise par réseau de neurones réduit-elle le risque extrême d’une option vendue par rapport à la couverture delta lorsque les rééquilibrages sont discrets et coûteux ?

**Données.** Trajectoires simulées et explicitement identifiées comme telles. Le modèle principal sera Black–Scholes ; la robustesse sera testée sous changement de volatilité et, si le temps de calcul le permet, sous volatilité stochastique de Heston.

**Atout.** Le sujet relie contrôle stochastique, risque, dérivés et deep learning. Il complète le mémoire existant : il s’agit ici d’apprendre une décision séquentielle, non de prévoir ou attribuer un P&L historique.

**Risque.** L’installation et le coût de calcul de PyTorch doivent être validés tôt. Le travail ne doit pas prétendre proposer un nouvel algorithme de deep hedging.

### B. Prévision dynamique de la VaR par quantiles

**Question envisagée.** Un réseau de quantiles améliore-t-il la calibration et l’indépendance des dépassements de VaR par rapport à la simulation historique et à CAViaR ?

**Données.** Rendements de marché réels. L’accès, la continuité historique et les droits de redistribution doivent être vérifiés avant toute publication.

**Atout.** Question directement liée au risque de marché, avec tests de Kupiec et de Christoffersen.

**Risque.** La dépendance à une source de données externe et la nécessité d’un historique assez long fragilisent la faisabilité en cinq jours. Une comparaison neuronale crédible exige aussi une validation temporelle soigneuse.

### C. Allocation robuste sous queues épaisses

**Question envisagée.** Dans quelle mesure une allocation minimisant la CVaR ou une formulation robuste de Wasserstein résiste-t-elle mieux qu’une allocation moyenne–variance à l’erreur d’estimation et aux queues épaisses ?

**Données.** Simulations multivariées contrôlées, complétées éventuellement par des rendements redistribuables.

**Atout.** Très forte composante d’optimisation, de gestion des risques et de robustesse statistique.

**Risque.** Le lien avec le deep learning appliqué à la finance est faible et la formulation robuste complète peut devenir trop large pour un premier cycle de cinq jours.

## Grille de notation

| Sujet | Science 20 % | Professionnel 20 % | Données 15 % | Littérature 10 % | Visuels 10 % | Faisabilité 15 % | Complémentarité 10 % | Score / 5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Deep hedging avec coûts | 5 | 5 | 5 | 5 | 5 | 4 | 4 | **4,75** |
| B. VaR dynamique par quantiles | 5 | 5 | 3 | 5 | 5 | 3 | 5 | **4,35** |
| C. Allocation robuste | 4 | 5 | 4 | 5 | 5 | 4 | 5 | **4,50** |

## Décision

Le sujet A est retenu. Son score est le plus élevé et il correspond exactement à la priorité professionnelle actuelle : le deep learning appliqué à la finance et à la gestion des risques. Les données simulées permettent de contrôler la vérité génératrice, de mesurer la robustesse et de publier un travail entièrement reproductible sans difficulté de licence.

Le type principal sera **Projet**. Le livrable n’aura pas le statut de publication scientifique évaluée par les pairs. Il sera présenté comme une étude computationnelle reproductible et comme une réplication critique, avec extension de sensibilité, de la littérature sur la couverture sous frictions.

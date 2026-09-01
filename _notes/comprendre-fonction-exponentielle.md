---
title: "La fonction exponentielle, de l’intuition au modèle"
summary: Pourquoi l’exponentielle apparaît-elle dès qu’une variation dépend de l’état présent ? Une exploration intuitive, mathématique et computationnelle, avec des applications en finance, en gestion des risques et en deep learning.
date: 2026-08-15
updated: 2026-09-01
tags:
  - Analyse
  - Modélisation
  - Calcul scientifique
search_terms: fonction exponentielle nombre e croissance décroissance logarithme intérêt composé taux continu calibration survie risque softmax deep learning logistique
comment_term: note-comprendre-fonction-exponentielle
---
## Une idée avant toute formule

Une évolution est dite **additive** lorsqu’elle gagne la même quantité à chaque étape. Elle est **multiplicative** lorsqu’elle est multipliée par le même facteur. C’est cette seconde logique qui conduit à l’exponentielle.

> **L’idée en une phrase.** Une quantité suit une dynamique exponentielle lorsque son taux de variation est proportionnel à sa valeur actuelle. Plus elle est grande, plus sa variation absolue est grande ; plus elle est petite, plus cette variation ralentit.

Cette note poursuit quatre objectifs : comprendre ce que l’exponentielle modélise, expliquer pourquoi la base \\(e\\) est naturelle, apprendre à interpréter et estimer son taux, puis reconnaître les situations où ce modèle devient insuffisant.

Partons de 100. Ajouter 10 à chaque période produit la suite \\(100,110,120,130,\ldots\\). Augmenter de 10 % produit plutôt \\(100,110,121,133{,}10,\ldots\\), car chaque hausse s’applique à une base déjà modifiée.

| Période \\(n\\) | Croissance additive \\(100+10n\\) | Croissance multiplicative \\(100(1{,}10)^n\\) |
| ---: | ---: | ---: |
| 0 | 100,00 | 100,00 |
| 1 | 110,00 | 110,00 |
| 2 | 120,00 | 121,00 |
| 3 | 130,00 | 133,10 |
| 4 | 140,00 | 146,41 |

Une courbe n’est donc pas exponentielle simplement parce qu’elle « monte vite ». Le critère essentiel est plus précis : **sur des intervalles de même durée, la quantité est multipliée par un facteur constant**.

Cette distinction peut aussi se lire localement. Dans un modèle exponentiel continu, ce n’est pas la variation absolue \\(y^{\prime}(t)\\) qui reste constante, mais la variation *relative* :

$$
\frac{y'(t)}{y(t)}=k.
$$

Autrement dit, gagner 5 unités n’a pas le même sens lorsque la quantité vaut 10 ou 10 000. En revanche, croître de 5 % décrit la même variation relative dans les deux cas.

## Du temps discret au temps continu

En temps discret, une quantité initiale \\(y_0\\) multipliée par \\(q\\) à chaque période suit

$$
y_n=y_0q^n.
$$

Pour décrire un phénomène en temps continu, on écrit plutôt

$$
y(t)=y_0e^{kt},
$$

où \\(k\\) est le **taux instantané**. Ces deux écritures sont compatibles. Pour un pas de temps \\(\Delta t\\),

$$
q=e^{k\Delta t}
\qquad\text{et donc}\qquad
k=\frac{\ln q}{\Delta t}.
$$

Cette relation évite une confusion fréquente : un taux effectif par période et un taux continu ne sont pas numériquement identiques, même lorsqu’ils représentent la même évolution.

Elle donne aussi un moyen direct de retrouver le taux continu à partir de deux observations positives. Si \\(y(t_1)=y_1\\) et \\(y(t_2)=y_2\\), alors

$$
k=\frac{\ln(y_2/y_1)}{t_2-t_1}.
$$

Par exemple, une quantité qui passe de 500 à 650 en quatre ans possède, sur cette période, un taux continu moyen

$$
k=\frac{\ln(650/500)}{4}\approx0{,}0656,
$$

soit environ 6,56 % par an en convention continue. Le facteur annuel correspondant est \\(e^k\approx1{,}0678\\), donc un taux effectif d’environ 6,78 %. Ce calcul décrit le taux constant qui relie exactement les deux points ; il ne prouve pas que le mécanisme est réellement exponentiel entre ces dates ou après elles.

L’exponentielle possède aussi une propriété structurelle remarquable :

$$
e^{k(t+s)}=e^{kt}e^{ks}.
$$

Faire évoluer le système pendant \\(t+s\\) revient à le faire évoluer pendant \\(t\\), puis pendant \\(s\\). Cette cohérence entre composition temporelle et multiplication explique pourquoi l’exponentielle apparaît naturellement dans les systèmes dynamiques.

## Pourquoi la base \\(e\\) ?

Le nombre

$$
e\approx2{,}718281828
$$

peut être approché par un problème de capitalisation. Un capital de 1 rémunéré à 100 % sur une année vaut 2 si l’intérêt est versé une seule fois. Si l’année est découpée en \\(n\\) périodes, avec un taux de \\(1/n\\) à chaque période, le capital final devient

$$
\left(1+\frac{1}{n}\right)^n.
$$

Lorsque la fréquence de capitalisation augmente indéfiniment,

$$
e=\lim_{n\to\infty}\left(1+\frac{1}{n}\right)^n.
$$

![Convergence de la capitalisation vers le nombre e](/assets/notes/fonction-exponentielle/capitalisation-continue.svg)

<p class="figure-caption">La capitalisation devient de plus en plus fréquente, mais la valeur obtenue sur une durée fixée converge vers \(e\) au lieu de diverger.</p>

Plus généralement, l’exponentielle peut être représentée par la série

$$
e^x=\sum_{n=0}^{\infty}\frac{x^n}{n!}
=1+x+\frac{x^2}{2!}+\frac{x^3}{3!}+\cdots.
$$

Cette série est à la fois une définition mathématique et un moyen de calculer numériquement l’exponentielle. Mais la propriété la plus importante pour la modélisation est

$$
\frac{d}{dx}e^x=e^x.
$$

La fonction est égale à sa propre dérivée : sa vitesse de variation est exactement proportionnelle à sa valeur.

## L’équation fondamentale de la croissance proportionnelle

Supposons qu’une quantité \\(y(t)\\) vérifie

$$
y'(t)=k\,y(t),
\qquad y(0)=y_0.
$$

La solution est

$$
y(t)=y_0e^{kt}.
$$

Cette équation dit que le changement instantané \\(y^{\prime}(t)\\) dépend de l’état actuel \\(y(t)\\). Elle fournit une grille de lecture simple des paramètres :

| Paramètre | Interprétation |
| --- | --- |
| \\(y_0\\) | valeur initiale, dans l’unité de la quantité étudiée |
| \\(k\\) | taux instantané, exprimé en inverse de l’unité de temps |
| \\(k>0\\) | croissance |
| \\(k<0\\) | décroissance |
| \\(\lvert k \rvert\\) élevé | évolution rapide |

L’unité de \\(k\\) est l’inverse de l’unité de temps. Si \\(t\\) est mesuré en années, \\(k\\) s’exprime en \\(\text{année}^{-1}\\). Le produit \\(kt\\) est ainsi sans unité, comme doit l’être l’argument d’une exponentielle.

![Croissance et décroissance exponentielles](/assets/notes/fonction-exponentielle/croissance-decroissance.svg)

<p class="figure-caption">Les fonctions \(e^x\) et \(e^{-x}\) sont positives et passent par \((0,1)\). Le signe du taux inverse le sens de l’évolution.</p>

Pour \\(k>0\\), le temps de doublement est obtenu en résolvant \\(e^{kt}=2\\) :

$$
t_{\mathrm{doublement}}=\frac{\ln 2}{k}.
$$

Pour \\(k<0\\), la demi-vie vaut

$$
t_{1/2}=\frac{\ln 2}{|k|}.
$$

Ces formules montrent qu’un taux et une durée caractéristique racontent la même dynamique sous deux angles différents.

## Exemple 1 — capitalisation et actualisation

Avec une capitalisation continue au taux \\(r\\), un capital \\(C_0\\) devient

$$
C(t)=C_0e^{rt}.
$$

Ainsi, 100 000 F CFA placés pendant dix ans à un taux continu de 5 % donnent

$$
C(10)=100\,000e^{0{,}05\times10}
\approx164\,872\ \text{F CFA}.
$$

Il ne faut pas confondre ce calcul avec un taux **effectif annuel** de 5 %, qui donnerait

$$
100\,000(1{,}05)^{10}\approx162\,889\ \text{F CFA}.
$$

Le taux continu équivalent à un taux effectif annuel \\(r_{\mathrm{eff}}\\) est

$$
r_c=\ln(1+r_{\mathrm{eff}}).
$$

Pour 5 %, on obtient \\(r_c=\ln(1{,}05)\approx4{,}879\%\\). Employer le bon taux est essentiel pour comparer correctement deux produits financiers.

L’opération inverse est l’actualisation. Une somme future \\(F\\), reçue dans \\(t\\) années, a pour valeur actuelle

$$
V_0=Fe^{-rt}.
$$

Le signe négatif ne traduit pas une perte mécanique : il ramène une valeur future à la date présente.

## Exemple 2 — risque, survie et temps d’attente

Dans un modèle de durée exponentiel, la fonction de survie est

$$
S(t)=\mathbb{P}(T>t)=e^{-\lambda t},
$$

où \\(\lambda>0\\) est un taux de survenue constant. La probabilité que l’événement se produise avant \\(t\\) est alors

$$
F(t)=1-e^{-\lambda t}.
$$

La durée moyenne vaut \\(1/\lambda\\), tandis que la durée médiane vaut \\(\ln(2)/\lambda\\). Ce modèle intervient, par exemple, comme première approximation d’un temps avant défaut, d’un temps de panne ou d’un délai entre événements.

Son hypothèse forte est la **constance du taux instantané de risque**. Si l’ancienneté, l’usure, la conjoncture ou le profil individuel modifient ce taux, une loi de Weibull, un modèle de Cox ou un modèle à intensité variable sera souvent plus pertinent.

## Exemple 3 — l’exponentielle dans le deep learning

Pour transformer des scores réels \\(z_1,\ldots,z_m\\) en probabilités, une couche de classification utilise souvent la fonction *softmax* :

$$
p_i=\frac{e^{z_i}}{\sum_{j=1}^{m}e^{z_j}}.
$$

Chaque probabilité est positive et leur somme vaut 1. Plus intéressant encore, le rapport entre deux probabilités est

$$
\frac{p_i}{p_j}=e^{z_i-z_j}.
$$

Une différence additive entre deux scores devient donc un rapport multiplicatif entre leurs probabilités. Pour les scores \\((2,1,0)\\), la softmax donne approximativement

$$
(0{,}665,\ 0{,}245,\ 0{,}090).
$$

En pratique, calculer directement \\(e^{z_i}\\) peut provoquer un dépassement numérique lorsque les scores sont grands. On soustrait donc le maximum \\(m=\max_i z_i\\) :

$$
p_i=\frac{e^{z_i-m}}{\sum_j e^{z_j-m}}.
$$

Cette transformation ne change pas les probabilités, mais stabilise fortement le calcul. C’est un exemple où comprendre l’identité algébrique de l’exponentielle conduit directement à une meilleure implémentation.

```python
import numpy as np

def softmax_stable(scores):
    scores = np.asarray(scores, dtype=float)
    scores_centres = scores - scores.max()
    poids = np.exp(scores_centres)
    return poids / poids.sum()

print(softmax_stable([2.0, 1.0, 0.0]))
# [0.66524096 0.24472847 0.09003057]
```

Le même principe apparaît dans la fonction *log-sum-exp*, fréquemment utilisée pour calculer des log-vraisemblances sans perdre en précision numérique.

## Le logarithme : lire et estimer une exponentielle

Le logarithme naturel \\(\ln\\) est la fonction réciproque de l’exponentielle :

$$
\ln(e^x)=x
\qquad\text{et}\qquad
e^{\ln x}=x\quad(x>0).
$$

Appliqué au modèle \\(y(t)=y_0e^{kt}\\), il donne

$$
\ln y(t)=\ln y_0+kt.
$$

Une relation exponentielle devient ainsi linéaire sur une échelle logarithmique. Si les points \\((t,\ln y_t)\\) sont approximativement alignés, cela constitue un indice en faveur d’un taux proportionnel constant.

Cette linéarisation n’est cependant pas une preuve. Elle exige des valeurs strictement positives et transforme aussi la structure des erreurs. Lorsque les observations sont bruitées, il faut comparer plusieurs modèles, examiner les résidus et évaluer les performances hors échantillon plutôt que se fier uniquement à l’aspect du graphe.

## Calcul numérique : deux détails qui comptent

Sur ordinateur, les formules mathématiquement équivalentes ne sont pas toujours numériquement équivalentes. Lorsque \\(x\\) est très proche de zéro, calculer \\(e^x-1\\) par `np.exp(x) - 1` soustrait deux nombres presque égaux et peut perdre des chiffres significatifs. NumPy fournit `np.expm1(x)` précisément pour ce cas. De même, `np.log1p(x)` calcule \\(\\ln(1+x)\\) avec davantage de précision lorsque \\(x\\) est petit.

```python
import numpy as np

taux_effectif = 0.05
taux_continu = np.log1p(taux_effectif)
taux_reconstitue = np.expm1(taux_continu)

print(taux_continu)     # 0.048790164...
print(taux_reconstitue) # 0.05, à la précision machine
```

Ce détail est utile dans les calculs de taux, de rendement, de vraisemblance et plus généralement dans les algorithmes manipulant de très petites variations.

## Quand l’exponentielle devient-elle irréaliste ?

Une exponentielle pure suppose qu’aucune contrainte ne ralentit durablement le mécanisme. Une population, une adoption technologique ou une production ne peut pourtant pas croître indéfiniment dans un environnement fini.

Le modèle logistique introduit une capacité \\(K\\) :

$$
y'(t)=r\,y(t)\left(1-\frac{y(t)}{K}\right).
$$

Lorsque \\(y(t)\\) est très inférieur à \\(K\\), le facteur \\(1-y/K\\) est proche de 1 et la croissance ressemble à une exponentielle. À mesure que \\(y(t)\\) approche \\(K\\), la croissance ralentit.

![Comparaison entre croissance exponentielle et croissance logistique](/assets/notes/fonction-exponentielle/exponentielle-logistique.svg)

<p class="figure-caption">Les deux modèles partent de la même valeur et du même taux initial. Le modèle exponentiel conserve ce taux proportionnel, tandis que le modèle logistique ralentit sous l’effet de la capacité \(K\).</p>

Voici un code Python minimal permettant de reproduire cette comparaison :

```python
import numpy as np
import matplotlib.pyplot as plt

t = np.linspace(0, 8, 300)
y0, r, K = 100, 0.35, 1_000

exponentielle = y0 * np.exp(r * t)
logistique = K / (1 + ((K - y0) / y0) * np.exp(-r * t))

fig, ax = plt.subplots(figsize=(9, 4.8))
ax.plot(t, exponentielle, label="Exponentielle", linewidth=2.5)
ax.plot(t, logistique, label="Logistique", linewidth=2.5)
ax.axhline(K, color="0.45", linestyle="--", label="Capacité K")
ax.set(xlabel="Temps", ylabel="Quantité", ylim=(0, 1_800))
ax.legend(frameon=False)
ax.grid(alpha=0.2)
plt.show()
```

Le graphe illustre une règle de modélisation importante : deux modèles peuvent être presque indiscernables au début de l’observation et produire des extrapolations radicalement différentes. Le choix ne doit donc pas reposer uniquement sur l’ajustement aux premières données, mais aussi sur le mécanisme supposé et sur une validation hors échantillon.

## Erreurs d’interprétation fréquentes

| Affirmation | Correction |
| --- | --- |
| « Une courbe qui augmente vite est exponentielle. » | Il faut vérifier un facteur multiplicatif ou un taux relatif approximativement constant. |
| « Un taux continu de 5 % équivaut à un taux effectif de 5 %. » | Le taux effectif correspondant est \\(e^{0{,}05}-1\\approx5{,}127\\%\\). |
| « Une exponentielle atteint zéro après un certain temps. » | Une décroissance \\(y_0e^{-kt}\\) reste strictement positive pour tout temps fini. |
| « Si le logarithme des données semble linéaire, le modèle est validé. » | C’est un diagnostic utile, pas une validation ; les résidus et la performance prédictive restent à examiner. |
| « Une tendance exponentielle peut être extrapolée indéfiniment. » | Toute extrapolation dépend du maintien du mécanisme, du taux et de l’absence de saturation ou de rupture. |

## Une courte histoire de \\(e\\)

Le nombre \\(e\\) n’est pas l’invention isolée d’un seul mathématicien. Les travaux sur les logarithmes au XVIIe siècle ont préparé le terrain. En 1683, Jacob Bernoulli rencontre la limite \\(\left(1+1/n\right)^n\\) en étudiant les intérêts composés. Leonhard Euler emploie ensuite la lettre \\(e\\) dans une lettre de 1731 et organise systématiquement ses propriétés dans son *Introductio in analysin infinitorum* de 1748.

Cette histoire éclaire le concept : l’exponentielle se situe au croisement des intérêts composés, des logarithmes, des séries et du calcul différentiel.

## Comment reconnaître un modèle exponentiel ?

Avant de retenir \\(y(t)=y_0e^{kt}\\), il est utile de vérifier les points suivants :

1. La quantité étudiée reste-t-elle positive ?
2. Le changement paraît-il proportionnel au niveau courant ?
3. Le facteur de croissance est-il approximativement stable sur des intervalles comparables ?
4. Le logarithme des observations est-il approximativement linéaire dans le temps ?
5. Existe-t-il une saturation, un changement de régime ou une contrainte structurelle ?
6. Le modèle prédit-il correctement des observations qui n’ont pas servi à l’estimer ?

Les quatre premières questions motivent l’exponentielle. Les deux dernières empêchent de l’utiliser par réflexe lorsqu’un modèle plus riche est nécessaire.

## À retenir

La fonction exponentielle traduit une règle locale simple : **la variation instantanée est proportionnelle à l’état présent**. Cette règle produit une dynamique multiplicative, relie naturellement temps discret et temps continu, et explique la présence de \\(e\\) en finance, en gestion des risques, dans les systèmes dynamiques et dans les réseaux de neurones.

Comprendre l’exponentielle, ce n’est donc pas seulement savoir calculer \\(e^x\\). C’est savoir identifier l’hypothèse qu’elle encode, interpréter son taux, reconnaître ses limites et choisir un autre modèle lorsque le mécanisme réel ne peut pas croître ou décroître à taux proportionnel constant.

## Références

- [NIST Digital Library of Mathematical Functions — Exponential and logarithmic functions](https://dlmf.nist.gov/4.2)
- [MacTutor History of Mathematics — The number e](https://mathshistory.st-andrews.ac.uk/HistTopics/e/)
- [MIT OpenCourseWare — The exponential function](https://ocw.mit.edu/ans7870/18/18.013a/textbook/HTML/chapter02/section01.html)
- [OpenStax Calculus — Exponential growth and decay](https://openstax.org/books/calculus-volume-2/pages/2-8-exponential-growth-and-decay)
- [NIST Engineering Statistics Handbook — Exponential distribution](https://www.itl.nist.gov/div898/handbook/apr/section1/apr161.htm)
- [PyTorch documentation — Softmax](https://docs.pytorch.org/docs/stable/generated/torch.nn.modules.activation.Softmax.html)

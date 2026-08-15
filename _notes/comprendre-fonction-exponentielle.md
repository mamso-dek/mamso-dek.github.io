---
title: "La fonction exponentielle : comprendre une croissance qui se multiplie"
summary: Une introduction concrète à l’exponentielle, à l’origine du nombre e et aux phénomènes de croissance ou de décroissance qu’elle permet de modéliser.
date: 2026-08-15
tags:
  - Analyse
  - Fonctions
  - Modélisation
search_terms: fonction exponentielle nombre e croissance décroissance logarithme intérêt composé dérivée demi-vie modélisation
comment_term: note-comprendre-fonction-exponentielle
---
## L’idée essentielle : multiplier plutôt qu’ajouter

Une évolution linéaire ajoute la même quantité à chaque étape. Une évolution exponentielle multiplie par le même facteur à intervalles réguliers.

Partons de 100. Si l’on ajoute 10 à chaque période, on obtient une progression linéaire. Si l’on augmente de 10 %, la hausse suivante est calculée sur une quantité déjà plus grande :

| Période | Ajout de 10 | Hausse de 10 % |
| ---: | ---: | ---: |
| 0 | 100 | 100 |
| 1 | 110 | 110 |
| 2 | 120 | 121 |
| 3 | 130 | 133,10 |
| 4 | 140 | 146,41 |

La différence paraît faible au début, puis elle s’amplifie. C’est le mécanisme cumulatif de l’exponentielle : **la variation dépend de ce qui est déjà présent**.

## Définition

Une fonction exponentielle s’écrit sous la forme

$$
f(x)=C\,a^x,
$$

où \\(C>0\\) est la valeur initiale, \\(a>0\\) est la base et \\(a\neq1\\). Lorsque \\(a>1\\), la fonction croît ; lorsque \\(0<a<1\\), elle décroît.

Son caractère exponentiel apparaît dans le rapport

$$
\frac{f(x+h)}{f(x)}=a^h.
$$

Pour un même intervalle \\(h\\), le facteur multiplicatif est toujours le même, quel que soit le point de départ \\(x\\). C’est cette propriété, et non le simple fait de « croître vite », qui définit une évolution exponentielle.

![Croissance et décroissance exponentielles](/assets/notes/fonction-exponentielle/croissance-decroissance.svg)

<p class="figure-caption">Les deux courbes restent positives et passent par le point (0, 1). La courbe \(e^x\) croît, tandis que \(e^{-x}\) décroît et se rapproche de zéro sans l’atteindre.</p>

## Pourquoi le nombre \\(e\\) apparaît-il ?

Le nombre

$$
e \approx 2{,}718281828
$$

est la base dite *naturelle* de l’exponentielle. Il apparaît lorsque l’on découpe une croissance en intervalles de plus en plus petits.

Imaginons un capital de 1 placé à un taux annuel de 100 %. Si l’intérêt est versé une seule fois, le capital final vaut 2. S’il est versé deux fois, chaque versement applique un taux de 50 % :

$$
\left(1+\frac{1}{2}\right)^2=2{,}25.
$$

Avec \\(n\\) versements au cours de l’année, le capital devient

$$
\left(1+\frac{1}{n}\right)^n.
$$

Lorsque les versements deviennent infiniment fréquents, cette quantité tend vers \\(e\\) :

$$
e=\lim_{n\to\infty}\left(1+\frac{1}{n}\right)^n.
$$

![Convergence de la capitalisation vers le nombre e](/assets/notes/fonction-exponentielle/capitalisation-continue.svg)

<p class="figure-caption">Augmenter la fréquence de capitalisation rapproche le résultat de \(e\), sans produire une croissance infinie sur une durée fixée.</p>

## D’où vient cette idée ?

L’histoire de \\(e\\) ne commence pas avec une formule unique. Les logarithmes développés au XVIIe siècle ont préparé le terrain, mais le nombre apparaît explicitement dans un autre problème. En 1683, Jacob Bernoulli étudie la capitalisation composée et encadre la limite de \\(\left(1+1/n\right)^n\\) entre 2 et 3.

Leibniz utilise en 1690 une lettre pour désigner ce nombre, sans employer la notation moderne. La lettre \\(e\\) apparaît dans une lettre de Leonhard Euler à Christian Goldbach en 1731. Euler rassemble ensuite, notamment dans son ouvrage de 1748, plusieurs propriétés aujourd’hui centrales : la limite précédente, le développement en série et le lien avec les logarithmes.

L’exponentielle n’a donc pas été « inventée » en une seule fois. Elle est née de la rencontre entre les logarithmes, les intérêts composés, les séries et le calcul différentiel.

## Pourquoi la base \\(e\\) est-elle naturelle ?

Parmi toutes les fonctions \\(a^x\\), la fonction \\(e^x\\) possède une propriété remarquable :

$$
\frac{d}{dx}e^x=e^x.
$$

Sa pente en chaque point est exactement égale à sa valeur. Si \\(e^x=5\\), sa pente vaut aussi 5 ; si \\(e^x=0{,}2\\), sa pente vaut 0,2.

Plus généralement, si une quantité \\(y(t)\\) varie à une vitesse proportionnelle à sa valeur actuelle,

$$
y'(t)=k\,y(t),
$$

alors sa trajectoire est

$$
y(t)=y_0e^{kt}.
$$

Le paramètre \\(k\\) est un taux instantané :

- \\(k>0\\) décrit une croissance ;
- \\(k<0\\) décrit une décroissance ;
- plus \\(|k|\\) est grand, plus l’évolution est rapide.

Voilà pourquoi \\(e^x\\) apparaît si souvent dans les équations différentielles : elle transforme la règle « la variation est proportionnelle à la quantité présente » en une formule explicite.

## Trois exemples concrets

### 1. Un capital placé

Un capital initial de 100 000 F CFA placé pendant dix ans à un taux continu de 5 % vaut

$$
C(10)=100\,000\,e^{0{,}05\times10}
\approx164\,872\ \text{F CFA}.
$$

Le modèle suppose ici que le taux reste constant. Dans la réalité, les frais, les impôts et les variations de taux doivent être ajoutés à l’analyse.

### 2. Une population qui double

Une culture contient initialement 500 bactéries et double toutes les trois heures. Son effectif peut s’écrire

$$
N(t)=500\,2^{t/3}
=500\,e^{(\ln 2/3)t}.
$$

Après douze heures, quatre doublements ont eu lieu :

$$
N(12)=500\times2^4=8\,000.
$$

Ce modèle est pertinent au début de la croissance. Il finit par devenir irréaliste lorsque les nutriments, l’espace ou d’autres ressources deviennent limitants.

### 3. Une décroissance radioactive

Si une substance possède une demi-vie de huit jours, la quantité restante après \\(t\\) jours est

$$
Q(t)=Q_0\,2^{-t/8}.
$$

Avec 80 mg au départ, il reste après 24 jours

$$
Q(24)=80\times2^{-3}=10\ \text{mg}.
$$

La même structure intervient dans de nombreux phénomènes de décroissance : désintégration radioactive, élimination simplifiée d’un médicament ou écart de température dans la loi de refroidissement de Newton.

## Le logarithme répond à la question inverse

L’exponentielle calcule une quantité future à partir du temps. Le logarithme naturel \\(\ln\\), fonction réciproque de \\(e^x\\), permet de retrouver le temps ou le taux :

$$
\ln(e^x)=x.
$$

Par exemple, le temps nécessaire pour doubler un capital soumis à un taux continu de 5 % vérifie

$$
2=e^{0{,}05t}
\quad\Longrightarrow\quad
t=\frac{\ln 2}{0{,}05}
\approx13{,}86\ \text{ans}.
$$

L’exponentielle et le logarithme forment donc un couple : l’une décrit l’évolution, l’autre permet de remonter à la durée ou au taux qui l’a produite.

## Où retrouve-t-on encore l’exponentielle ?

Elle intervient notamment :

- dans les probabilités, par exemple dans la densité de la loi normale ;
- dans les systèmes dynamiques et les équations différentielles ;
- dans le traitement du signal et les circuits électriques ;
- dans les modèles de survie et les temps d’attente ;
- dans la finance, pour l’actualisation et la capitalisation ;
- dans les modèles matriciels, via l’exponentielle de matrice.

Le point commun n’est pas toujours une croissance spectaculaire. C’est souvent une loi locale simple : **à chaque instant, le changement dépend de l’état présent**.

## Quand ne faut-il pas utiliser ce modèle ?

Une exponentielle pure suppose un taux proportionnel constant et l’absence de contrainte de capacité. Elle devient inadéquate lorsque :

- le taux évolue fortement dans le temps ;
- une population approche une capacité maximale ;
- une intervention extérieure modifie le mécanisme ;
- plusieurs régimes se succèdent ;
- les observations ne conservent pas un facteur multiplicatif à intervalles comparables.

Dans ces situations, un modèle logistique, un modèle par morceaux ou un système dynamique plus riche peut être préférable.

## À retenir

La fonction exponentielle n’est pas seulement « une courbe qui monte très vite ». Elle décrit une évolution dans laquelle la même proportion s’applique de manière répétée. La base \\(e\\) devient naturelle lorsque cette évolution est pensée en temps continu, car \\(e^x\\) est sa propre dérivée. C’est cette combinaison entre multiplication, continuité et taux proportionnel qui explique sa présence dans autant de domaines.

## Pour aller plus loin

- [Histoire du nombre e - MacTutor, Université de St Andrews](https://mathshistory.st-andrews.ac.uk/HistTopics/e/)
- [The Exponential Function - MIT OpenCourseWare](https://ocw.mit.edu/ans7870/18/18.013a/textbook/HTML/chapter02/section01.html)
- [Exponential Growth and Decay - OpenStax Calculus](https://openstax.org/books/calculus-volume-2/pages/2-8-exponential-growth-and-decay)

# Rolling

Server side of [rolling](https://redbricks.games/home/rolling-117) game. See [rollgui](https://github.com/buxx/rollgui) for client side.

![Rollgui screenshot](https://redbricks.games/uploads/117/game/Coffee_231_illustration.png)

# Installation

A python3.7+ is required. If you use debian, debian 10 is required if you want to use OS python packaged. But you can compile python3.7 on your system.

Following documentation assume you use debian 10 or simial OS. You will need:

    apt-get install git python3 python3-venv build-essential python3-dev

## Python environment require

If you need to create a virtual environment, you can use the following:

    python3 -m venv venv

Then activate it in current terminal with:

    source venv/bin/activate

To install required python packages:

    pip install --upgrade pip setuptools
    pip install -r requirements.txt
    python setup.py develop

Then install dev packages:

    pip install -e ".[dev]"

## Generate a map

Need [Rust](https://www.rust-lang.org/learn/get-started)

Write a text file (ex. myworldmap.txt) containg, for example:

```
::LEGEND
~ SEA*
^ MOUNTAIN
ፆ JUNGLE
∩ HILL
⡩ BEACH
⠃ PLAIN
::META
SPAWN:RANDOM:BEACH,
::GEO
~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~ፆ^ፆፆ~~~~~~~~~~~~
~~~~~~~~ፆ^^^∩ፆ~~~~~~~~~~~
~~~~~~~⡩ፆ∩∩∩∩⡩~~~~~~~~~~~
~~~~~~⡩ፆፆ∩∩∩ፆፆ⡩~~~~~~~~~~
~~~~~~⡩ፆፆፆፆፆፆፆ⡩~~~~~~~~~~
~~~~~~⡩⠃⠃⠃ፆፆፆፆ⡩~~~~~~~~~~
~~~~~~⡩⠃⠃⠃⠃⠃⠃⡩~~~~~~~~~~~
~~~~~~~⡩⠃⠃⠃⠃⡩~~~~~~~~~~~~
~~~~~~~~⡩⡩⡩⡩~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~
```

Then, generate zones maps:

    cargo run myworldmap.txt --height 64 --width 64 --output-dir myzones

## Start server

    rolling-server --host 127.0.0.1 --port 5002 --debug ./myworldmap.txt ./myzones ./game

Where `./myworldmap.txt` is previously created world map text file, `./myzones` previously generated zones folder and `./game` the config folder (you can use [repository folder](https://github.com/buxx/rolling/tree/master/game) or copied and modified one).

## Use docker image

To build docker image:

    docker build . -t rolling:latest

To run server:

    docker run -v <local path containing world.txt>:/world -v <local path containing zones>:/zones -v <local path containing game config>:/game -v -v <local path for db>:/db rolling:latest

# Roadmap (fr)

Pour participer, rendez-vous sur la page des [briques](https://redbricks.games/home/rolling-117/bricks).

* Légende
  * ☐ A faire
  * ☑ Fait
  * **prochaines fonctionnalités développées**

* Bugs
  * ☐ **des footer_links n'apparaissent pas (ex. lien fiche sur follow)**

* Bases
  * ☑ Création personnage
  * ☑ Mécanisme de caractéristiques et compétences
  * ☑ Génération de carte du monde
  * ☑ Déplacements sur les zones
  * ☑ Types de tuiles (roche, herbe, eau, etc)
  * ☑ Voyage d'une zone à l'autre
  * ☑ Gestion d'objets
  * ☑ Gestion de ressources
  * ☐ Réserve/Evolutions/Exploitation de ressources par zone (renouvellement et consommation)
  * ☑ Mécanisme de base de gestion/fabrication de batiments d'une tuile (mur, feux, etc)
  * ☐ Mécanisme de gestion/fabrication de batiments de plusieurs tuiles (grenier, pont)
  * ☑ Ecran de chat de zone
  * ☑ Ecran de chat de groupes
  * ☐ Ecran de chat d'affinités
  * ☑ Propositions commerciales permanentes
  * ☑ Propositions commerciales uniques
  * ☑ Mécanisme de base de l'histoire du personnage (livre)
  * ☐ Peupler le jeu d'évènement pour le l'histoire du personnage
  * ☐ Participation à plusieurs de la rédaction de l'histoire (récits)
  * ☐ Etendre une construction (ex. cave de stockage) (tuiles côtes-a-côtes)
  * ☑ Batiments qui empeche le mouvement (ex. murs)
  * ☐ Batiments permettant de conserver la nourriture
  * ☑ Page zone, afficher 1 bouton par affinité appartenu avec au moins un perso dans la zone
  * ☐ Interdire la construction au bord de la zone (pour permettre les voyages)
  * ☐ Phase test 2: poisson fumé; bois sur plage (peu)
  * ☑ Retirer de la fatigue au passage de tour

* Actions
  * ☑ Ramasser un objet
  * ☑ Rammasser des resources
  * ☑ Chercher de la nourriture (exploitation des ressources nourriture de la zone)
  * ☑ Mélanger des ressources (eau + terre = terre mouillé)
  * ☑ Exploiter des ressources (bois, pierre, etc)
  * ☑ Construire un objet à partir de ressources
  * ☑ Construire un objet à partir d'objets
  * ☑ Transformer une ressource en une autre
  * ☑ Remplir/vider un objet (ex. eau dans bouteille)
  * ☑ Attaquer un/des personnages
  * ☑ Boire/Manger un objet/ressource
  * ☑ Utiliser des objets comme arme/bouclier/armure
  * ☑ Ranger/Stocker des resources dans un batiment
  * ☐ Ranger/Stocker des objets dans un batiment
  * ☑ Tuer un personnage
  * ☑ Donner des objets/ressources à un autre personnage
  * ☑ Prendre des objets/ressources d'un autre personnage
  * ☐ Voler un autre personnage
  * ☐ Voler dans un batiment (si protégé)
  * ☐ Tenter d'assassiner un autre personnage (tenter d'échaper a la défense de groupe)
  * ☐ Verrouillage de porte (en entrant ou sortant ou totu le temps, etc)
  * ☐ Verrouillage de serrures + clefs (coffre, porte, etc)
  * ☐ Dégrader/casser un bâtiment
  * ☐ Proposer de rejoindre une affinité
  * ☐ Proposer de suivre
  * ☐ Proposer de faire une action a un autre perso
  * ☐ Cultures
  * ☐ Chasse: Proposer des actions groupés sur les animaux (transformation en viande, peau, etc)
  * ☐ Généraliser l'usage de craft par progression d'ap mais pouvoir simplifier/en faire plusieurs d'affilé en une dépense

* Gameplay
  * ☐ Restreindre l'accès a des informations comme l'existence des affinités, nom de zone, etc et permettre leurs transmissions
  * ☐ Blessures, maladies, effets
  * ☐ Usure des objets et bâtiments
  * ☐ Automatisation de tâches / processus
  * ☐ Restreindre des accès avec son personnage
  * ☐ Restreindre l'usage de bâtiments
  * ☐ Maintient en fonctionnement des bâtiments (ex: alimenter un feu en bois pour le passage de tour)
  * ☐ PA des bâtiments (pour l'usage à plusieurs)
  * ☐ Mécanismes de monaie
  * ☐ Nommer des lieux (ex. pour déclarer une ville dans une zone)
  * ☑ Acquérir une connaissance seul
  * ☑ Acquérir une connaissance avec un formateur
  * ☑ Déplacements en groupe (suivre) lors de changement de zones
  * ☐ Cacher des objets/ressources et chercher aux alentours
  * ☐ % de perte au combat: a l'attaque, interruption. A la defense, fuite.
  * ☐ Fuite lors d'une defense: charisme/compétence permet de ne pas voir les combattant fuir n'importe-où
  * ☐ Worldmap non visible là ou pas visité (et pas été visible)
  * ☐ Possibilité de déclarer des quêtes (ress/obj/asassinat/?)
  * ☐ Visibilité des affinités uniquement si dans la zone en cours
  * ☐ Effets négatifs du meurtres (TODO conception)
  * ☐ Déclarer la guerre entre affinités
  * ☐ Gestion du sommeil
  * ☐ Animaux (serveur d'IA)
  * ☐ Capture d'animaux (ex. déplacement vers parc; murs non traversable par animaux)
  * ☐ Débourrage (pour animaux de monte)
  * ☐ Monte d'animaux (véhicules)
  * ☐ Remorques
  * ☐ Le poids transporté influent sur les durées de déplacement au lieu de l'empếcher "au gramme près"
  * ☐ Météo et influence sur les actions (hiver = peu de nourriture !)
  * ☐ Péromption des aliments (avec influence du stockage: sac, grenier, jarre, etc)
  * ☐ Regain de points de vies au passage de tour
  * ☐ Modifier l'environnement: ex. creuser des tranchés (eau qui coule)
  * ☐ **Inventaire/Affinité: pouvoir donner accès à son inventaire à une/des affinités**
  * ☐ Depuis l'inventaire, accès aux ressources/objets disponible à travers les affinités (inventaires des persos, bâtiments, protectorat)
  * ☐ Protectorat
  * ☐ Pouvoir qualifier un personnage (ex. le bon, le fou, le gros, etc) après avoir assez cottoyé, et en faire le nom publique si beaucoup partagé.
  * ☐ Pouvoir se cacher
  * ☐ Accords: non aggression, échange de valeurs (produits vs PA), etc
  * ☐ **De quoi manger/boire: prendre en compte ce qui est au sol**
  * ☐ De quoi manger/boire: prendre en compte ce qui est partagé par les affinités
  * ☐ Signaler (au sein d'une affinité) un perso comme recherché (mort/vif) genre voleur

* Univers
  * ☑ Décors de base
  * ☐ Caractéristiques et compétences accordés avec gameplay
  * ☐ Choix du design de l'univers pour le serveur "modèle"
  * ☐ Ajouter une grande quantité d'objets, ressources, implémentation d'actions, bâtiments pour peupler l'univers du serveur "modèle"
  * ☐ Générateur d'avatar (voir piou-piou)
  * ☐ Générateur de décors (illustration zones)
  * ☐ Présentation du serveur configurable (affiché à la création du personnage)
  * ☐ Ajouter des objets en végétaux tressés (action restreinte a certaines type de zones)

* Fonctionnalités extras
  * ☐ Historiser les déplacements (world map) de tous les personnages pour fabriquer des cartes démographiques
  * ☐ Ajouter une dimension "hauteur" pour pouvoir creuser des galleries
  * ☐ Modification de l'environnement (creuser pour rediriger l'eau, douves, etc)
  * ☐ Permettre l'ajout de personnages non humain (IA/transformation depuis personnage joué)

* Ergonomie de l'interface
  * ☐ Musique/Ambiance sonore
  * ☐ **Images dans l'histoire du personnage (GUI)**
  * ☐ Images pour les objets
  * ☐ Images pour les ressources
  * ☐ Images pour les bâtiments
  * ☐ Images pour les personnages (upload ?)
  * ☐ Intégration des chats (zone, groupes, etc) sur l'écran de déplacement
  * ☐ Click sur tuile: ouverture de page d'actions
  * ☐ Les actions qui nécessaite une position (ex. à coté de) envoient une requête de déplacement au GUI avant de s'éxecuter
  * ☐ Affichage dans l'écran de Zone les nouvelles prop. commerciales, invit°, etc
  * ☑ Afficher si à manger dans la zone (sidebar)
  * ☑ Afficher combien de combattant protègent dans la zone (sidebar)

* Mécanique serveur
  * ☐ Contrôle des positions pour les actions (prendre, attaquer corps-à-corps/distance, etc)
  * ☐ Contrôle de la visibilité pour les actions à distance (ex. attaque à l'arc vs mur)

* Optimisation/Changements serveur
  * ☐ Connexions serveur async
  * ☐ Passage à PostgreSQL
  * ☐ Calcul de "a boire", "a manger", "protégé par" calculés par websockets (perf)

* Gestion du serveur
  * ☐ Conversion txt -> pixel RGB des cartes
  * ☐ Carte zones compilés

* Hors-jeu
  * ☐ Pages de scores: zones les plus habités
  * ☐ Pages de scores: zones les plus civilisés (constructions/qualités)
  * ☐ Pages de scores: démographies (+historisation pour carte)
  * ☐ Pages de scores: combativité (+historisation pour carte)
  * ☐ Pages de scores: mortalité (+historisation pour carte)
  * ☐ Outils de gestion pour les maitres du jeu

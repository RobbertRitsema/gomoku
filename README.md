
My implementation of MCTS for gomoku.


version:

v1.1 Het werkt nu ook als het boad een numpy array is.
V1.2 Full fledged gomoku game rules.
V1.3 Restrictions on second move lifted.
v1.4 Gebruik overal (row,col) om moves te representeren. Geen (x,y) meer.
v1.5 GmQuickTests toegevoegd.
v1.6 GmGame retourneert nu het empty tuple () als initiele last_move (ipv None) 
     - conform het gedrag van gomoku competition, checklist geupdate (correctie: zwart=2 en O).
v1.61 GmQuickTest initialiseert player voor de test op de juiste kleur via new_game.
v1.62 gomoku_ai_marius1_webclient werkte bij nieuwere python versies niet meer in competition.
      Dat is nu gefixed.
      Verder meer tests toegevoegd, ook tests waarbij je AI als wit speelt
v1.63 de webclients kunnen nu eventueel ook op kleinere borden deelnemen aan de competitie.
v1.64 gomoku_ai_marius_tng_webclient toegevoegd
      GmQuickTest genereerde gaf niet de juiste (last_move) mee voor de tests
      waarbij je ai met wit speelt. Dat is nu gefixed.
      GmGame is robust gemaakt tegen ai's die de input gamestate aanpassen.
      Color codes in GmGame was reversed. Ooops. Dat is nu gefixed.
      GmGame gebruikt nu niet veel cpu tijd meer tussen de games in.
      Extra advanced test example toegevoegd aan GmQuickTest
      competition is verbeterd: robuust tegen ai's die een exception genereren.
      de overtreder wordt bij name genoemd en gepenalized.
      De competition hoeft er niet voor onderbroken te worden.

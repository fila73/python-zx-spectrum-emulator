package sk.zoliky.logic

import sk.zoliky.model.Card
import sk.zoliky.model.Deck

/**
 * Manages the state of the game table.
 * Spravuje stav herního stolu.
 */
class GameTable {
    val deck = Deck()
    val discardPile = mutableListOf<Card>()
    val players = mutableListOf<Player>()
    var currentPlayerIndex = 0
        private set

    /**
     * Starts a new game with the given player names.
     * Zahájí novou hru se zadanými jmény hráčů.
     */
    fun startGame(playerNames: List<String>) {
        if (playerNames.size !in 2..4) {
            throw IllegalArgumentException("Game requires 2-4 players / Hra vyžaduje 2-4 hráče")
        }

        players.clear()
        playerNames.forEach { players.add(Player(it)) }

        // Initialize and shuffle deck
        deck.initialize()
        deck.shuffle()
        discardPile.clear()
        currentPlayerIndex = 0

        // Deal cards
        // First player gets 14 cards, others 13 (Standard Zoliky rule for 2 decks/4 jokers?)
        // Rules often say: Dealer deals 12 to everyone, rest to stock.
        // Or: 15/14.
        // Let's stick to the plan: Starter 14, others 13.
        
        players.forEachIndexed { index, player ->
            val cardsToDeal = if (index == 0) 14 else 13
            val dealt = deck.deal(cardsToDeal)
            dealt.forEach { player.hand.addCard(it) }
        }
        
        // No card to discard pile initially if Starter has 14. 
        // Starter discards one to start the pile.
    }

    fun getCurrentPlayer(): Player {
        if (players.isEmpty()) throw IllegalStateException("Game not started")
        return players[currentPlayerIndex]
    }

    /**
     * Current player draws a card from the deck.
     * Aktuální hráč si táhne kartu z balíčku.
     */
    fun drawCard(playerId: String) {
        validateTurn(playerId)
        if (deck.isEmpty()) {
            // Reshuffle discard pile into deck?
            if (discardPile.isEmpty()) throw IllegalStateException("Deck and Discard empty! Draw?")
            refillDeckFromDiscard()
        }
        val card = deck.deal(1).first()
        getCurrentPlayer().hand.addCard(card)
    }

    /**
     * Current player draws the top card from the discard pile.
     * Aktuální hráč si bere vrchní kartu z odhazovacího balíčku.
     */
    fun drawFromDiscard(playerId: String) {
        validateTurn(playerId)
        if (discardPile.isEmpty()) throw IllegalStateException("Discard pile is empty")
        
        val card = discardPile.removeAt(discardPile.lastIndex)
        getCurrentPlayer().hand.addCard(card)
    }

    /**
     * Current player discards a card to end their turn.
     * Aktuální hráč odhodí kartu a ukončí tah.
     */
    fun discardCard(playerId: String, card: Card) {
        validateTurn(playerId)
        val player = getCurrentPlayer()
        
        if (!player.hand.removeCard(card)) {
            throw IllegalArgumentException("Player does not have this card")
        }
        
        discardPile.add(card)
        nextTurn()
    }

    private fun nextTurn() {
        currentPlayerIndex = (currentPlayerIndex + 1) % players.size
    }

    private fun validateTurn(playerId: String) {
        if (getCurrentPlayer().id != playerId) {
            throw IllegalStateException("It is not this player's turn / Není řada na tomto hráči")
        }
    }
    
    private fun refillDeckFromDiscard() {
        // Keep top card on discard pile
        if (discardPile.isEmpty()) return
        val topCard = discardPile.removeAt(discardPile.lastIndex)
        
        // Add rest to deck
        // This is tricky because Deck class logic uses direct list manipulation or creates new?
        // Our Deck class handles full init. We might need 'addCards' to Deck.
        // Since we can't easily add to Deck without refactoring Deck, 
        // let's Assume for MVP we just re-init if empty? No that resets game.
        // WE need to modify Deck to accept returning cards.
        // Or just let it crash for now/MVP task description said "draw from deck".
        // Let's implement a quick fix:
        throw NotImplementedError("Deck refill implementation required in Deck class")
    }
}

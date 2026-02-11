package sk.zoliky.model

/**
 * Represents a deck of cards for Žolíky.
 * Contains 108 cards (2 standard decks + 4 Jokers).
 * Reprezentuje balíček karet pro Žolíky.
 * Obsahuje 108 karet (2 standardní balíčky + 4 Žolíci).
 */
class Deck {
    private val cards = mutableListOf<Card>()

    init {
        initialize()
    }

    /**
     * Initializes the deck with 108 cards.
     * Inicializuje balíček se 108 kartami.
     */
    fun initialize() {
        cards.clear()
        // Two standard decks / Dva standardní balíčky
        repeat(2) {
            for (suit in Suit.values()) {
                if (suit == Suit.NONE) continue // Skip NONE for standard cards
                for (rank in Rank.values()) {
                    if (rank == Rank.JOKER) continue // Skip JOKER for standard cards
                    cards.add(Card(suit, rank))
                }
            }
        }
        // 4 Jokers / 4 Žolíci
        repeat(4) {
            cards.add(Card(Suit.NONE, Rank.JOKER))
        }
    }

    /**
     * Shuffles the deck.
     * Zamíchá balíček.
     */
    fun shuffle() {
        cards.shuffle()
    }

    /**
     * Deals a specific number of cards from the top of the deck.
     * Rozdá určitý počet karet z vrchu balíčku.
     *
     * @param count Number of cards to deal. / Počet karet k rozdání.
     * @return List of dealt cards. / Seznam rozdaných karet.
     * @throws IllegalArgumentException if not enough cards in deck.
     */
    fun deal(count: Int): List<Card> {
        if (count > cards.size) {
            throw IllegalArgumentException("Not enough cards in the deck / Nedostatek karet v balíčku")
        }
        val dealtCards = cards.takeLast(count)
        repeat(count) {
            cards.removeAt(cards.lastIndex)
        }
        return dealtCards
    }

    /**
     * Returns the current number of cards in the deck.
     * Vrací aktuální počet karet v balíčku.
     */
    fun size(): Int {
        return cards.size
    }

    /**
     * Returns true if the deck is empty.
     * Vrací true, pokud je balíček prázdný.
     */
    fun isEmpty(): Boolean {
        return cards.isEmpty()
    }
}

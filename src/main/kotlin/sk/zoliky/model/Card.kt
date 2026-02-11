package sk.zoliky.model

/**
 * Represents a playing card with a suit and a rank.
 * Reprezentuje hrací kartu s barvou a hodnotou.
 */
data class Card(
    val suit: Suit,
    val rank: Rank
) {
    override fun toString(): String {
        return "${rank.name} of ${suit.name}"
    }

    /**
     * Checks if this card is a Joker.
     * Zkontroluje, zda je tato karta Žolík.
     */
    fun isJoker(): Boolean {
        return rank == Rank.JOKER
    }
}
